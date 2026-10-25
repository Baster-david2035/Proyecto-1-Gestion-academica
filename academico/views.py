from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Carrera, Curso, PeriodoLectivo, Grupo
from .serializers import (
    CarreraSerializer,
    CursoSerializer,
    PeriodoLectivoSerializer,
    GrupoSerializer,
)

from usuarios.views import es_administrador, obtener_rol


def puede_modificar_academico(usuario):
    return es_administrador(usuario)


def responder_lista(request, queryset, serializer_class):
    """
    Aplica búsqueda, ordenamiento y paginación a una lista.
    """
    busqueda = request.query_params.get("search")

    if busqueda:
        campos = [
            campo.name
            for campo in queryset.model._meta.fields
            if campo.get_internal_type() in (
                "CharField",
                "TextField",
            )
        ]

        filtros = Q()

        for campo in campos:
            filtros |= Q(**{f"{campo}__icontains": busqueda})

        if filtros:
            queryset = queryset.filter(filtros)

    ordering = request.query_params.get("ordering")

    if ordering:
        campo = ordering.lstrip("-")

        campos_validos = {
            campo_modelo.name
            for campo_modelo in queryset.model._meta.fields
        }

        if campo not in campos_validos:
            return Response(
                {"error": "El campo de ordenamiento no es válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.order_by(ordering)

    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if page < 1 or page_size < 1:
            raise ValueError

        page_size = min(page_size, 50)

    except (ValueError, TypeError):
        return Response(
            {"error": "page y page_size deben ser enteros positivos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    total = queryset.count()
    inicio = (page - 1) * page_size
    resultados = queryset[inicio:inicio + page_size]

    serializer = serializer_class(resultados, many=True)

    return Response({
        "count": total,
        "page": page,
        "page_size": page_size,
        "results": serializer.data,
    })


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_carreras(request):
    if request.method == "GET":
        queryset = Carrera.objects.all()
        return responder_lista(request, queryset, CarreraSerializer)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede crear carreras."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CarreraSerializer(data=request.data)

    if serializer.is_valid():
        objeto = serializer.save()

        return Response(
            CarreraSerializer(objeto).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)

    if request.method == "GET":
        return Response(CarreraSerializer(carrera).data)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede modificar carreras."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ("PUT", "PATCH"):
        serializer = CarreraSerializer(
            carrera,
            data=request.data,
            partial=request.method == "PATCH",
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    if carrera.curso_set.exists():
        return Response(
            {"error": "No se puede eliminar una carrera que tiene cursos asociados."},
            status=status.HTTP_409_CONFLICT,
        )

    carrera.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_cursos(request):
    if request.method == "GET":
        queryset = Curso.objects.all()

        carrera_id = request.query_params.get("carrera")

        if carrera_id:
            queryset = queryset.filter(carrera_id=carrera_id)

        return responder_lista(request, queryset, CursoSerializer)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede crear cursos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = CursoSerializer(data=request.data)

    if serializer.is_valid():
        objeto = serializer.save()

        return Response(
            CursoSerializer(objeto).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    if request.method == "GET":
        return Response(CursoSerializer(curso).data)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede modificar cursos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ("PUT", "PATCH"):
        serializer = CursoSerializer(
            curso,
            data=request.data,
            partial=request.method == "PATCH",
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    curso.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_periodos(request):
    if request.method == "GET":
        queryset = PeriodoLectivo.objects.all()

        return responder_lista(
            request,
            queryset,
            PeriodoLectivoSerializer,
        )

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede crear períodos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = PeriodoLectivoSerializer(data=request.data)

    if serializer.is_valid():
        objeto = serializer.save()

        return Response(
            PeriodoLectivoSerializer(objeto).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_periodo(request, pk):
    periodo = get_object_or_404(PeriodoLectivo, pk=pk)

    if request.method == "GET":
        return Response(PeriodoLectivoSerializer(periodo).data)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede modificar períodos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ("PUT", "PATCH"):
        serializer = PeriodoLectivoSerializer(
            periodo,
            data=request.data,
            partial=request.method == "PATCH",
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    periodo.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_grupos(request):
    if request.method == "GET":
        queryset = Grupo.objects.all()

        curso_id = request.query_params.get("curso")
        periodo_id = request.query_params.get("periodo")

        if curso_id:
            queryset = queryset.filter(curso_id=curso_id)

        if periodo_id:
            queryset = queryset.filter(periodo_id=periodo_id)

        return responder_lista(request, queryset, GrupoSerializer)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede crear grupos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = GrupoSerializer(data=request.data)

    if serializer.is_valid():
        objeto = serializer.save()

        return Response(
            GrupoSerializer(objeto).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_grupo(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)

    if request.method == "GET":
        return Response(GrupoSerializer(grupo).data)

    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede modificar grupos."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ("PUT", "PATCH"):
        serializer = GrupoSerializer(
            grupo,
            data=request.data,
            partial=request.method == "PATCH",
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    grupo.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
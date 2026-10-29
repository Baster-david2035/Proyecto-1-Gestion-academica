from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import (api_view,authentication_classes,permission_classes)
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

def puede_ver_academico(usuario):
    """
    Administradores, profesores y estudiantes pueden ver (GET).
    """
    if not usuario.is_authenticated:
        return False
    rol = obtener_rol(usuario)
    return rol in ["ADMINISTRADOR", "PROFESOR", "ESTUDIANTE", "ADMIN"]


def puede_modificar_academico(usuario, metodo):
    """
    Controla quién puede hacer POST, PUT, PATCH o DELETE:
    - Administrador: Control total sobre todo.
    - Profesor: Puede crear o actualizar ciertos registros (ej. crear grupos o cursos), pero no borrar.
    - Estudiante: No puede modificar nada por esta vía (solo ver o matricularse).
    """
    if not usuario.is_authenticated:
        return False
        
    rol = obtener_rol(usuario)
    
    # 1. El administrador puede hacer absolutamente todo
    if rol in ["ADMINISTRADOR", "ADMIN"] or usuario.is_superuser or usuario.is_staff:
        return True
        
    # 2. Permisos para el profesor
    if rol == "PROFESOR":
        # Permitimos crear o actualizar (POST, PUT, PATCH), pero prohibimos eliminar (DELETE)
        if metodo in ["POST", "PUT", "PATCH"]:
            return True
        return False
        
    # 3. Los estudiantes no tienen permisos de modificación por esta vía
    return False


def obtener_id_filtro(request, parametro):
    valor = request.query_params.get(parametro)
    if not valor:
        return None, None
    try:
        identificador = int(valor)
        if identificador < 1:
            raise ValueError
        return identificador, None
    except (TypeError, ValueError):
        return None, Response(
            {parametro: "Debe ser un entero positivo."},
            status=status.HTTP_400_BAD_REQUEST,
        )


# Función genérica reutilizable para aplicar búsqueda por texto, ordenamiento dinámico y paginación a cualquier queryset
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
        campo = ordering[1:] if ordering.startswith("-") else ordering
        campos_validos = {
            campo_modelo.name
            for campo_modelo in queryset.model._meta.fields
        }

        if not campo or campo.startswith("-") or "," in ordering or campo not in campos_validos:
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


# ==========================================
# VISTAS DE CARRERAS
# ==========================================

@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_carreras(request):
    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver las carreras."}, status=status.HTTP_403_FORBIDDEN)
        queryset = Carrera.objects.all()
        return responder_lista(request, queryset, CarreraSerializer)

    # Validar con la nueva función que incluye el request.method
    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios suficientes para crear carreras."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CarreraSerializer(data=request.data)
    if serializer.is_valid():
        objeto = serializer.save()
        return Response(CarreraSerializer(objeto).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_carrera(request, pk):
    carrera = get_object_or_404(Carrera, pk=pk)

    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver esta carrera."}, status=status.HTTP_403_FORBIDDEN)
        return Response(CarreraSerializer(carrera).data)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios para modificar o eliminar carreras."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ("PUT", "PATCH"):
        serializer = CarreraSerializer(carrera, data=request.data, partial=request.method == "PATCH")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    if carrera.cursos.exists():
        return Response({"error": "No se puede eliminar una carrera que tiene cursos asociados."}, status=status.HTTP_409_CONFLICT)

    carrera.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# VISTAS DE CURSOS
# ==========================================

@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_cursos(request):
    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver los cursos."}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = Curso.objects.all()
        carrera_id, error = obtener_id_filtro(request, "carrera")
        if error:
            return error
        if carrera_id is not None:
            queryset = queryset.filter(carrera_id=carrera_id)

        return responder_lista(request, queryset, CursoSerializer)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios suficientes para crear cursos."}, status=status.HTTP_403_FORBIDDEN)

    serializer = CursoSerializer(data=request.data)
    if serializer.is_valid():
        objeto = serializer.save()
        return Response(CursoSerializer(objeto).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_curso(request, pk):
    curso = get_object_or_404(Curso, pk=pk)

    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver este curso."}, status=status.HTTP_403_FORBIDDEN)
        return Response(CursoSerializer(curso).data)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios para modificar o eliminar cursos."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ("PUT", "PATCH"):
        serializer = CursoSerializer(curso, data=request.data, partial=request.method == "PATCH")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    curso.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# VISTAS DE PERIODOS LECTIVOS
# ==========================================

@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_periodos(request):
    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver los períodos."}, status=status.HTTP_403_FORBIDDEN)
        queryset = PeriodoLectivo.objects.all()
        return responder_lista(request, queryset, PeriodoLectivoSerializer)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios suficientes para crear períodos."}, status=status.HTTP_403_FORBIDDEN)

    serializer = PeriodoLectivoSerializer(data=request.data)
    if serializer.is_valid():
        objeto = serializer.save()
        return Response(PeriodoLectivoSerializer(objeto).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_periodo(request, pk):
    periodo = get_object_or_404(PeriodoLectivo, pk=pk)

    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver este período."}, status=status.HTTP_403_FORBIDDEN)
        return Response(PeriodoLectivoSerializer(periodo).data)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios para modificar o eliminar períodos."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ("PUT", "PATCH"):
        serializer = PeriodoLectivoSerializer(periodo, data=request.data, partial=request.method == "PATCH")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    periodo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


# ==========================================
# VISTAS DE GRUPOS
# ==========================================

@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_grupos(request):
    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver los grupos."}, status=status.HTTP_403_FORBIDDEN)
        
        queryset = Grupo.objects.all()
        curso_id, error = obtener_id_filtro(request, "curso")
        if error:
            return error
        periodo_id, error = obtener_id_filtro(request, "periodo")
        if error:
            return error
        if curso_id is not None:
            queryset = queryset.filter(curso_id=curso_id)
        if periodo_id is not None:
            queryset = queryset.filter(periodo_id=periodo_id)

        return responder_lista(request, queryset, GrupoSerializer)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios suficientes para crear grupos."}, status=status.HTTP_403_FORBIDDEN)

    serializer = GrupoSerializer(data=request.data)
    if serializer.is_valid():
        objeto = serializer.save()
        return Response(GrupoSerializer(objeto).data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_grupo(request, pk):
    grupo = get_object_or_404(Grupo, pk=pk)

    if request.method == "GET":
        if not puede_ver_academico(request.user):
            return Response({"error": "No tienes permisos para ver este grupo."}, status=status.HTTP_403_FORBIDDEN)
        return Response(GrupoSerializer(grupo).data)

    if not puede_modificar_academico(request.user, request.method):
        return Response({"error": "No tienes privilegios para modificar o eliminar grupos."}, status=status.HTTP_403_FORBIDDEN)

    if request.method in ("PUT", "PATCH"):
        serializer = GrupoSerializer(grupo, data=request.data, partial=request.method == "PATCH")
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    grupo.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
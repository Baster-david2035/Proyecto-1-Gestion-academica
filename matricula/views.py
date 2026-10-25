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

from .models import Matricula
from .serializers import MatriculaSerializer

from usuarios.views import es_administrador, obtener_rol


def matriculas_visibles(usuario):
    queryset = Matricula.objects.select_related(
        "estudiante",
        "grupo",
    )

    if es_administrador(usuario):
        return queryset

    rol = obtener_rol(usuario)

    if rol == "ESTUDIANTE":
        return queryset.filter(estudiante=usuario)

    if rol == "PROFESOR":
        return queryset.filter(grupo__profesor=usuario)

    return queryset.none()


def responder_matriculas(request, queryset):
    estado = request.query_params.get("estado")

    if estado:
        queryset = queryset.filter(estado__iexact=estado)

    grupo_id = request.query_params.get("grupo")

    if grupo_id:
        queryset = queryset.filter(grupo_id=grupo_id)

    busqueda = request.query_params.get("search")

    if busqueda:
        queryset = queryset.filter(
            Q(estudiante__username__icontains=busqueda)
            | Q(estudiante__first_name__icontains=busqueda)
            | Q(estudiante__last_name__icontains=busqueda)
        )

    try:
        pagina = int(request.query_params.get("page", 1))
        tamano = int(request.query_params.get("page_size", 10))

        if pagina < 1 or tamano < 1:
            raise ValueError

        tamano = min(tamano, 50)

    except (TypeError, ValueError):
        return Response(
            {"error": "page y page_size deben ser enteros positivos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    total = queryset.count()
    inicio = (pagina - 1) * tamano

    serializer = MatriculaSerializer(
        queryset[inicio:inicio + tamano],
        many=True,
    )

    return Response({
        "count": total,
        "page": pagina,
        "page_size": tamano,
        "results": serializer.data,
    })


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_matriculas(request):
    if request.method == "GET":
        queryset = matriculas_visibles(request.user)

        return responder_matriculas(request, queryset)

    rol = obtener_rol(request.user)

    if not es_administrador(request.user) and rol != "ESTUDIANTE":
        return Response(
            {"error": "Solo un estudiante o administrador puede matricular."},
            status=status.HTTP_403_FORBIDDEN,
        )

    datos = request.data.copy()

    if rol == "ESTUDIANTE":
        datos["estudiante"] = request.user.pk

    serializer = MatriculaSerializer(data=datos)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    matricula = serializer.save()

    return Response(
        MatriculaSerializer(matricula).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_matricula(request, pk):
    matricula = get_object_or_404(
        matriculas_visibles(request.user),
        pk=pk,
    )

    if request.method == "GET":
        return Response(MatriculaSerializer(matricula).data)

    if not es_administrador(request.user):
        return Response(
            {"error": "Solo un administrador puede modificar matrículas."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method in ("PUT", "PATCH"):
        serializer = MatriculaSerializer(
            matricula,
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

    matricula.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
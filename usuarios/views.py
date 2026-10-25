from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.models import PerfilUsuario
from usuarios.serializers import PerfilUsuarioSerializer


def obtener_rol(usuario):
    """
    Obtiene el rol del usuario desde su perfil.
    Si es superusuario, lo considera administrador.
    """
    if usuario.is_superuser or usuario.is_staff:
        return "ADMINISTRADOR"

    try:
        perfil = PerfilUsuario.objects.get(usuario=usuario)
        return str(perfil.rol).upper()
    except PerfilUsuario.DoesNotExist:
        return "SIN_ROL"


def es_administrador(usuario):
    """
    Comprueba si el usuario tiene permisos de administrador.
    """
    return usuario.is_authenticated and (
        usuario.is_superuser
        or usuario.is_staff
        or obtener_rol(usuario) == "ADMINISTRADOR"
    )


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mi_perfil(request):
    """
    Permite consultar el perfil del usuario autenticado.
    """
    try:
        perfil = PerfilUsuario.objects.get(usuario=request.user)
    except PerfilUsuario.DoesNotExist:
        return Response(
            {"error": "El usuario no tiene un perfil registrado."},
            status=status.HTTP_404_NOT_FOUND,
        )

    serializer = PerfilUsuarioSerializer(perfil)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_perfiles(request):
    """
    Permite al administrador consultar todos los perfiles.
    """
    if not es_administrador(request.user):
        return Response(
            {"error": "No tiene permisos para consultar todos los perfiles."},
            status=status.HTTP_403_FORBIDDEN,
        )

    perfiles = PerfilUsuario.objects.select_related("usuario").all()
    serializer = PerfilUsuarioSerializer(perfiles, many=True)

    return Response(serializer.data, status=status.HTTP_200_OK)

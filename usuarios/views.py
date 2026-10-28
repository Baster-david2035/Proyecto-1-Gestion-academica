from rest_framework import status
from rest_framework.decorators import (api_view,authentication_classes,permission_classes)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import PerfilUsuario
from .serializers import PerfilUsuarioSerializer


def obtener_rol(usuario):
    """
    Función auxiliar para obtener el rol del usuario desde su perfil 
    o determinarlo a partir de los permisos nativos de Django.
    """
    # Si el usuario es superusuario o staff de Django, se le asigna directamente el rol de ADMINISTRADOR
    if usuario.is_superuser or usuario.is_staff:
        return "ADMINISTRADOR"

    try:
        # Intenta buscar el perfil asociado al usuario en la base de datos
        perfil = PerfilUsuario.objects.get(user=usuario)
        # Retorna el rol definido en el perfil convertido a mayúsculas
        return str(perfil.rol).upper()
    except PerfilUsuario.DoesNotExist:
        # Si no tiene un perfil creado, retorna "SIN_ROL"
        return "SIN_ROL"


def es_administrador(usuario):
    """
    Función auxiliar para comprobar si un usuario cuenta con privilegios de administrador.
    """
    # Si el usuario no ha iniciado sesión / no está autenticado, no puede ser administrador
    if not usuario.is_authenticated:
        return False

    # Retorna True si es superusuario, staff, o si su rol evaluado con la función anterior es ADMIN/ADMINISTRADOR
    return (usuario.is_superuser or usuario.is_staff
        or obtener_rol(usuario) in ("ADMIN", "ADMINISTRADOR"))


# Vista de la API para consultar el perfil del usuario que está haciendo la petición actualmente
@api_view(["GET"])
@authentication_classes([TokenAuthentication])  # Requiere autenticación mediante Token Bearer/Token Auth
@permission_classes([IsAuthenticated])         # Exige que el usuario haya iniciado sesión obligatoriamente
def mi_perfil(request):
    """
    Consulta el perfil del usuario autenticado.
    """
    try:
        # Busca el perfil asociado al usuario autenticado (request.user)
        perfil = PerfilUsuario.objects.get(user=request.user)
    except PerfilUsuario.DoesNotExist:
        # Si el perfil no existe, responde con un código HTTP 404 (No encontrado) y un mensaje de error
        return Response(
            {"error": "El usuario no tiene un perfil registrado."},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Serializa la instancia del perfil para convertirla en un formato JSON legible
    serializer = PerfilUsuarioSerializer(perfil)

    # Retorna los datos serializados con un código HTTP 200 (Éxito)
    return Response(serializer.data,status=status.HTTP_200_OK)


# Vista de la API para listar todos los perfiles del sistema (restringida a administradores)
@api_view(["GET"])
@authentication_classes([TokenAuthentication])  # Requiere autenticación por Token
@permission_classes([IsAuthenticated])         # Exige que esté autenticado antes de evaluar los permisos manuales
def listar_perfiles(request):
    """
    Permite al administrador consultar todos los perfiles.
    """
    # Valida si el usuario actual cumple con los requisitos de administrador
    if not es_administrador(request.user):
        # Si no es administrador, deniega el acceso con un código HTTP 403 (Prohibido)
        return Response(
            {"error": "No tiene permisos para consultar todos los perfiles."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Obtiene todos los perfiles optimizando la consulta a la base de datos con select_related para traer el 'usuario' en una sola consulta
    perfiles = PerfilUsuario.objects.select_related("user").all()

    # Serializa la lista completa de perfiles (many=True indica que se procesa un queryset/conjunto de elementos)
    serializer = PerfilUsuarioSerializer(perfiles,many=True)

    # Retorna la lista serializada con un código HTTP 200 (Éxito)
    return Response(serializer.data,status=status.HTTP_200_OK)
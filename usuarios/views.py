from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import BasePermission, IsAuthenticated
from .models import PerfilUsuario
from .serializers import PerfilUsuarioSerializer

def es_administrador(usuario):
    if not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    try:
        return usuario.perfilusuario.rol == "ADMIN"
    except PerfilUsuario.DoesNotExist:
        return False

class PermisoPerfilUsuario(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return es_administrador(request.user)

    def has_object_permission(self, request, view, obj):
        if es_administrador(request.user):
            return True

        return (
            request.method in ("GET", "HEAD", "OPTIONS")
            and obj.user_id == request.user.id
        )


def es_administrador(usuario):
    if not usuario.is_authenticated:
        return False

    if usuario.is_superuser:
        return True

    try:
        return usuario.perfilusuario.rol == "ADMIN"
    except PerfilUsuario.DoesNotExist:
        return False


class PermisoPerfilUsuario(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return es_administrador(request.user)

    def has_object_permission(self, request, view, obj):
        if es_administrador(request.user):
            return True

        return (
            request.method in ("GET", "HEAD", "OPTIONS")
            and obj.user_id == request.user.id
        )


class PerfilUsuarioViewSet(viewsets.ModelViewSet):

    serializer_class = PerfilUsuarioSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, PermisoPerfilUsuario]

    def get_queryset(self):
        usuario = self.request.user

        if es_administrador(usuario):
            return PerfilUsuario.objects.select_related("user").all()

        return PerfilUsuario.objects.select_related("user").filter(
            user=usuario
        )


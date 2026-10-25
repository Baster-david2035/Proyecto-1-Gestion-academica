from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import Matricula
from .serializers import MatriculaSerializer
from .views import es_administrador, obtener_rol


class PaginacionMatricula(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50

class PermisoMatricula(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        if es_administrador(request.user):
            return True

        # El estudiante puede solicitar su propia matrícula.
        return (
            obtener_rol(request.user) == "ESTUDIANTE"
            and request.method == "POST"
        )

    def has_object_permission(self, request, view, obj):
        if es_administrador(request.user):
            return True

        rol = obtener_rol(request.user)

        if rol == "ESTUDIANTE":
            return (
                request.method in ("GET", "HEAD", "OPTIONS")
                and obj.estudiante_id == request.user.id
            )

        if rol == "PROFESOR":
            return (
                request.method in ("GET", "HEAD", "OPTIONS")
                and obj.grupo.profesor_id == request.user.id
            )

        return False


class MatriculaViewSet(viewsets.ModelViewSet):
    serializer_class = MatriculaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, PermisoMatricula]
    pagination_class = PaginacionMatricula
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "estudiante__username",
        "estudiante__first_name",
        "estudiante__last_name",
        "grupo__curso__nombre",
    ]
    ordering_fields = ["fecha_matricula", "estado"]
    ordering = ["-fecha_matricula"]

    def get_queryset(self):
        queryset = Matricula.objects.select_related(
            "estudiante",
            "grupo",
            "grupo__curso",
            "grupo__periodo",
            "grupo__profesor",
        )

        usuario = self.request.user
        rol = obtener_rol(usuario)

        if es_administrador(usuario):
            pass
        elif rol == "ESTUDIANTE":
            queryset = queryset.filter(estudiante=usuario)
        elif rol == "PROFESOR":
            queryset = queryset.filter(grupo__profesor=usuario)
        else:
            return queryset.none()

        grupo_id = self.request.query_params.get("grupo")
        estado = self.request.query_params.get("estado")

        if grupo_id:
            queryset = queryset.filter(grupo_id=grupo_id)

        if estado:
            queryset = queryset.filter(estado__iexact=estado)

        return queryset

    def perform_create(self, serializer):
        usuario = self.request.user

        if es_administrador(usuario):
            serializer.save()
            return

        if obtener_rol(usuario) != "ESTUDIANTE":
            raise PermissionDenied(
                "Solo los estudiantes y administradores pueden crear matrículas."
            )

        serializer.save(estudiante=usuario)    
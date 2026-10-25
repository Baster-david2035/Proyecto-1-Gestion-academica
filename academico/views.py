from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import Carrera, Curso, PeriodoLectivo, Grupo
from .serializers import (
    CarreraSerializer,
    CursoSerializer,
    PeriodoLectivoSerializer,
    GrupoSerializer,
)
from usuarios.views import es_administrador, obtener_rol


class PaginacionAcademica(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50


class PermisoAcademico(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        if request.method in ("GET", "HEAD", "OPTIONS"):
            return True

        return es_administrador(request.user)


class CarreraViewSet(viewsets.ModelViewSet):
    queryset = Carrera.objects.all().order_by("nombre")
    serializer_class = CarreraSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, PermisoAcademico]
    pagination_class = PaginacionAcademica
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codigo", "nombre"]
    ordering_fields = ["codigo", "nombre"]
    ordering = ["nombre"]


class CursoViewSet(viewsets.ModelViewSet):
    serializer_class = CursoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, PermisoAcademico]
    pagination_class = PaginacionAcademica
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["codigo", "nombre", "carrera__nombre"]
    ordering_fields = ["codigo", "nombre", "creditos"]
    ordering = ["nombre"]

    def get_queryset(self):
        queryset = Curso.objects.select_related("carrera").prefetch_related(
            "prerrequisitos"
        )

        carrera_id = self.request.query_params.get("carrera")
        creditos = self.request.query_params.get("creditos")

        if carrera_id:
            queryset = queryset.filter(carrera_id=carrera_id)

        if creditos:
            queryset = queryset.filter(creditos=creditos)

        return queryset


class PeriodoLectivoViewSet(viewsets.ModelViewSet):
    serializer_class = PeriodoLectivoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, PermisoAcademico]
    pagination_class = PaginacionAcademica
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre"]
    ordering_fields = ["nombre", "fecha_inicio", "fecha_fin"]
    ordering = ["-fecha_inicio"]

    def get_queryset(self):
        queryset = PeriodoLectivo.objects.all()

        activo = self.request.query_params.get("activo")
        if activo is not None:
            if activo.lower() in ("true", "1", "si"):
                queryset = queryset.filter(activo=True)
            elif activo.lower() in ("false", "0", "no"):
                queryset = queryset.filter(activo=False)

        return queryset


class GrupoViewSet(viewsets.ModelViewSet):
    serializer_class = GrupoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, PermisoAcademico]
    pagination_class = PaginacionAcademica
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "curso__nombre",
        "curso__codigo",
        "periodo__nombre",
        "profesor__username",
    ]
    ordering_fields = ["numero_grupo", "cupo_maximo"]
    ordering = ["curso__nombre", "numero_grupo"]

    def get_queryset(self):
        queryset = Grupo.objects.select_related(
            "curso", "periodo", "profesor"
        )

        rol = obtener_rol(self.request.user)

        if rol == "PROFESOR":
            queryset = queryset.filter(profesor=self.request.user)

        curso_id = self.request.query_params.get("curso")
        periodo_id = self.request.query_params.get("periodo")
        profesor_id = self.request.query_params.get("profesor")

        if curso_id:
            queryset = queryset.filter(curso_id=curso_id)

        if periodo_id:
            queryset = queryset.filter(periodo_id=periodo_id)

        if profesor_id and es_administrador(self.request.user):
            queryset = queryset.filter(profesor_id=profesor_id)

        return queryset

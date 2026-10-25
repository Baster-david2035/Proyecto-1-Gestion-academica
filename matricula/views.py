from rest_framework import viewsets, filters
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import BasePermission, IsAuthenticated

from .models import Matricula
from .serializers import MatriculaSerializer
from usuarios.views import es_administrador, obtener_rol


class PaginacionMatricula(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 50
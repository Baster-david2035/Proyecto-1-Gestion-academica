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
    # Captura el parámetro de búsqueda desde la URL (ej: ?search=ingenieria)
    busqueda = request.query_params.get("search")

    if busqueda:
        # Detecta automáticamente todos los campos de tipo CharField o TextField del modelo para buscar en ellos
        campos = [
            campo.name
            for campo in queryset.model._meta.fields
            if campo.get_internal_type() in (
                "CharField",
                "TextField",
            )
        ]

        filtros = Q()

        # Construye una consulta OR dinámicamente para buscar la cadena en cada uno de los campos de texto
        for campo in campos:
            filtros |= Q(**{f"{campo}__icontains": busqueda})

        if filtros:
            queryset = queryset.filter(filtros)

    # Captura el parámetro de ordenamiento desde la URL (ej: ?ordering=nombre o ?ordering=-fecha_inicio)
    ordering = request.query_params.get("ordering")

    if ordering:
        # Elimina el signo menos inicial (si existe) para validar puramente el nombre del campo en el modelo
        campo = ordering[1:] if ordering.startswith("-") else ordering

        # Obtiene un conjunto con los nombres válidos de todos los campos del modelo
        campos_validos = {
            campo_modelo.name
            for campo_modelo in queryset.model._meta.fields
        }

        # Valida si el campo solicitado para ordenar realmente existe en el modelo
        if not campo or campo.startswith("-") or "," in ordering or campo not in campos_validos:
            return Response(
                {"error": "El campo de ordenamiento no es válido."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = queryset.order_by(ordering)

    # Bloque protegido para procesar la paginación (número de página y elementos por página)
    try:
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 10))

        if page < 1 or page_size < 1:
            raise ValueError

        # Limita el tamaño máximo de la página a 50 elementos para proteger el rendimiento
        page_size = min(page_size, 50)

    except (ValueError, TypeError):
        return Response(
            {"error": "page y page_size deben ser enteros positivos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Calcula el total de registros encontrados y los límites de la porción (slice) para la página actual
    total = queryset.count()
    inicio = (page - 1) * page_size
    resultados = queryset[inicio:inicio + page_size]

    # Serializa el subconjunto de resultados obtenidos
    serializer = serializer_class(resultados, many=True)

    # Retorna la respuesta estructurada con metadatos de paginación y los resultados
    return Response({
        "count": total,
        "page": page,
        "page_size": page_size,
        "results": serializer.data,
    })


# Vista de API para listar (GET) y crear (POST) Carreras
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])  # Requiere autenticación por token
@permission_classes([IsAuthenticated])         # Exige sesión activa
def listar_crear_carreras(request):
    
    # Manejo de petición GET: lista las carreras aplicando búsqueda, orden y paginación
    if request.method == "GET":
        queryset = Carrera.objects.all()
        return responder_lista(request, queryset, CarreraSerializer)

    # Valida que el usuario tenga privilegios para crear registros académicos
    if not puede_modificar_academico(request.user):
        return Response(
            {"error": "Solo un administrador puede crear carreras."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Valida y guarda la nueva carrera enviada en el request
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


# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) una Carrera específica por su ID (pk)
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

    # Regla de negocio: No se puede eliminar una carrera si tiene cursos asociados (retorna conflicto HTTP 409)
    if carrera.cursos.exists():
        return Response(
            {"error": "No se puede eliminar una carrera que tiene cursos asociados."},
            status=status.HTTP_409_CONFLICT,
        )

    carrera.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


# Vista de API para listar (GET) y crear (POST) Cursos
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_cursos(request):
    
    # Manejo de petición GET: lista y permite filtrar por carrera opcionalmente (?carrera=ID)
    if request.method == "GET":
        queryset = Curso.objects.all()

        carrera_id, error = obtener_id_filtro(request, "carrera")
        if error:
            return error
        if carrera_id is not None:
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


# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) un Curso específico por su ID (pk)
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


# Vista de API para listar (GET) y crear (POST) Periodos Lectivos
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


# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) un Periodo Lectivo específico por su ID (pk)
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


# Vista de API para listar (GET) y crear (POST) Grupos académicos
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_grupos(request):
    
    # Manejo de petición GET: lista y permite filtrar por curso (?curso=ID) o periodo (?periodo=ID) de forma opcional
    if request.method == "GET":
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


# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) un Grupo específico por su ID (pk)
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

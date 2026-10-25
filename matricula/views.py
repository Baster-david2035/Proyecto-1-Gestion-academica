from django.shortcuts import get_object_or_404
from django.db.models import Q

from rest_framework import status
from rest_framework.decorators import (api_view,authentication_classes,permission_classes)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Matricula
from .serializers import MatriculaSerializer
from usuarios.views import es_administrador, obtener_rol


# Función auxiliar para filtrar qué matrículas puede ver un usuario según su rol y permisos
def matriculas_visibles(usuario):
    # Obtiene el queryset base optimizado con select_related para traer los datos del estudiante y el grupo en una sola consulta
    queryset = Matricula.objects.select_related(
        "estudiante",
        "grupo",
    )

    # Si el usuario es administrador, puede ver absolutamente todas las matrículas del sistema
    if es_administrador(usuario):
        return queryset

    # Obtiene el rol específico del usuario (ej: ESTUDIANTE, PROFESOR)
    rol = obtener_rol(usuario)

    # Si es un estudiante, solo puede ver sus propias matrículas
    if rol == "ESTUDIANTE":
        return queryset.filter(estudiante=usuario)

    # Si es un profesor, solo puede ver las matrículas de los grupos que él imparte
    if rol == "PROFESOR":
        return queryset.filter(grupo__profesor=usuario)

    # Si no tiene un rol válido o reconocido, no se le muestra ninguna matrícula (queryset vacío)
    return queryset.none()


# Función auxiliar encargada de aplicar filtros por parámetros (estado, grupo, búsqueda de texto) y paginación
def responder_matriculas(request, queryset):
    # Filtro opcional por estado de la matrícula mediante parámetros GET (ej: ?estado=MATRICULADO)
    estado = request.query_params.get("estado")
    if estado:
        queryset = queryset.filter(estado__iexact=estado)

    # Filtro opcional por ID de grupo mediante parámetros GET (ej: ?grupo=3)
    grupo_id = request.query_params.get("grupo")
    if grupo_id:
        queryset = queryset.filter(grupo_id=grupo_id)

    # Filtro opcional de búsqueda por texto (username, nombre o apellido del estudiante)
    busqueda = request.query_params.get("search")
    if busqueda:
        queryset = queryset.filter(
            Q(estudiante__username__icontains=busqueda)
            | Q(estudiante__first_name__icontains=busqueda)
            | Q(estudiante__last_name__icontains=busqueda)
        )

    # Bloque protegido para procesar los parámetros de paginación (número de página y tamaño de página)
    try:
        pagina = int(request.query_params.get("page", 1))
        tamano = int(request.query_params.get("page_size", 10))

        # Valida que los números de página o tamaño no sean negativos o cero
        if pagina < 1 or tamano < 1:
            raise ValueError

        # Limita el tamaño máximo de elementos por página a 50 para proteger el rendimiento de la API
        tamano = min(tamano, 50)

    except (TypeError, ValueError):
        # Si envían valores no numéricos o inválidos, responde con un error HTTP 400
        return Response(
            {"error": "page y page_size deben ser enteros positivos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Calcula el total de registros encontrados después de aplicar los filtros
    total = queryset.count()
    # Calcula el índice inicial para recortar el queryset según la página solicitada
    inicio = (pagina - 1) * tamano

    # Serializa únicamente el fragmento (slice) correspondiente a la página actual
    serializer = MatriculaSerializer(
        queryset[inicio:inicio + tamano],
        many=True,
    )

    # Retorna una respuesta estructurada con los metadatos de paginación y los resultados
    return Response({
        "count": total,
        "page": pagina,
        "page_size": tamano,
        "results": serializer.data,
    })


# Vista de API para listar matrículas (GET) y crear una nueva matrícula (POST)
@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])  # Requiere autenticación mediante Token Bearer
@permission_classes([IsAuthenticated])         # Exige que el usuario haya iniciado sesión
def listar_crear_matriculas(request):
    
    # Manejo de peticiones GET: listar las matrículas permitidas para el usuario actual
    if request.method == "GET":
        queryset = matriculas_visibles(request.user)
        return responder_matriculas(request, queryset)

    # Manejo de peticiones POST: creación de una matrícula
    rol = obtener_rol(request.user)

    # Valida permisos: solo un administrador o un estudiante pueden realizar matrículas
    if not es_administrador(request.user) and rol != "ESTUDIANTE":
        return Response(
            {"error": "Solo un estudiante o administrador puede matricular."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Copia los datos enviados en la petición para poder modificarlos si es necesario
    datos = request.data.copy()

    # Si el que matricula es un estudiante, se fuerza automáticamente a que el estudiante sea el usuario autenticado
    if rol == "ESTUDIANTE":
        datos["estudiante"] = request.user.pk

    # Pasa los datos al serializer para validarlos
    serializer = MatriculaSerializer(data=datos)

    if not serializer.is_valid():
        # Si los datos son inválidos, retorna los errores con código HTTP 400
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Guarda la nueva matrícula en la base de datos
    matricula = serializer.save()

    # Retorna los datos de la matrícula creada con el código HTTP 201 (Creado exitosamente)
    return Response(
        MatriculaSerializer(matricula).data,
        status=status.HTTP_201_CREATED,
    )


# Vista de API para ver el detalle (GET), actualizar (PUT/PATCH) o eliminar (DELETE) una matrícula específica
@api_view(["GET", "PUT", "PATCH", "DELETE"])
@authentication_classes([TokenAuthentication])  # Requiere autenticación por Token
@permission_classes([IsAuthenticated])         # Exige que el usuario esté autenticado
def detalle_matricula(request, pk):
    
    # Busca la matrícula asegurándose de que pertenezca al conjunto de elementos visibles para el usuario (restringiendo accesos ajenos)
    matricula = get_object_or_404(
        matriculas_visibles(request.user),
        pk=pk,
    )

    # Manejo de petición GET: retorna el detalle individual de la matrícula
    if request.method == "GET":
        return Response(MatriculaSerializer(matricula).data)

    # Para modificar o eliminar, las reglas de este sistema exigen permisos exclusivos de administrador
    if not es_administrador(request.user):
        return Response(
            {"error": "Solo un administrador puede modificar matrículas."},
            status=status.HTTP_403_FORBIDDEN,
        )

    # Manejo de peticiones PUT (reemplazo completo) o PATCH (actualización parcial)
    if request.method in ("PUT", "PATCH"):
        serializer = MatriculaSerializer(
            matricula,
            data=request.data,
            partial=request.method == "PATCH",  # Si es PATCH, permite actualizar solo algunos campos
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Manejo de petición DELETE: elimina el registro de la matrícula de la base de datos
    matricula.delete()

    # Retorna una respuesta exitosa sin contenido (código HTTP 204)
    return Response(status=status.HTTP_204_NO_CONTENT)
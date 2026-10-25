from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Evaluacion, Calificacion
from .serializers import EvaluacionSerializer, CalificacionSerializer


# Vista de API para listar (GET) y crear (POST) evaluaciones de un grupo
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])  # Exige token de autenticación
@permission_classes([IsAuthenticated])         # Exige que el usuario haya iniciado sesión
def listar_crear_evaluaciones(request):

    # Manejo de peticiones GET: lista y filtra las evaluaciones registradas
    if request.method == 'GET':
        # Optimiza la consulta trayendo el grupo relacionado en una sola consulta a la base de datos
        evaluaciones = Evaluacion.objects.select_related('grupo').all()

        # Captura el parámetro opcional 'grupo' desde la URL (ej: ?grupo=2)
        grupo_id = request.query_params.get('grupo')

        if grupo_id:
            evaluaciones = evaluaciones.filter(grupo_id=grupo_id)

        # Ordena los resultados por ID de grupo y nombre de la evaluación alfabéticamente
        evaluaciones = evaluaciones.order_by('grupo_id', 'nombre')

        serializer = EvaluacionSerializer(evaluaciones, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Manejo de peticiones POST: creación de una nueva evaluación
    serializer = EvaluacionSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        # Retorna la evaluación creada con el código HTTP 201 (Creado exitosamente)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    # Si los datos no son válidos, retorna los errores con código HTTP 400
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) una evaluación específica por su ID (pk)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_evaluacion(request, pk):

    # Intenta buscar la evaluación, manejando el caso de que no exista (retorna HTTP 404)
    try:
        evaluacion = Evaluacion.objects.select_related('grupo').get(pk=pk)
    except Evaluacion.DoesNotExist:
        return Response(
            {'error': 'La evaluación no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Manejo de petición GET: retorna el detalle individual de la evaluación
    if request.method == 'GET':
        serializer = EvaluacionSerializer(evaluacion)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Manejo de peticiones PUT (reemplazo completo) o PATCH (actualización parcial)
    if request.method in ['PUT', 'PATCH']:
        serializer = EvaluacionSerializer(
            evaluacion,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Manejo de petición DELETE: elimina la evaluación de la base de datos
    evaluacion.delete()

    # Retorna una respuesta exitosa sin contenido (código HTTP 204)
    return Response(status=status.HTTP_204_NO_CONTENT)


# Vista de API para listar (GET) y registrar (POST) calificaciones de los estudiantes
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_calificaciones(request):

    # Manejo de peticiones GET: lista y filtra las calificaciones registradas
    if request.method == 'GET':
        # Optimiza la consulta trayendo la matrícula, el estudiante y la evaluación relacionada
        calificaciones = Calificacion.objects.select_related(
            'matricula__estudiante',
            'evaluacion',
        ).all()

        # Captura parámetros opcionales de filtrado en la URL (?matricula=X o ?evaluacion=Y)
        matricula_id = request.query_params.get('matricula')
        evaluacion_id = request.query_params.get('evaluacion')

        if matricula_id:
            calificaciones = calificaciones.filter(
                matricula_id=matricula_id,
            )

        if evaluacion_id:
            calificaciones = calificaciones.filter(
                evaluacion_id=evaluacion_id,
            )

        # Ordena cronológicamente por matrícula y evaluación
        calificaciones = calificaciones.order_by(
            'matricula_id',
            'evaluacion_id',
        )

        serializer = CalificacionSerializer(calificaciones, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Manejo de peticiones POST: creación de una nueva calificación
    serializer = CalificacionSerializer(data=request.data)

    if serializer.is_valid():
        datos = serializer.validated_data

        matricula = datos['matricula']
        evaluacion = datos['evaluacion']
        nota = datos['nota_obtenida']

        # Regla de negocio 1: Validar que la nota esté dentro del rango permitido (0 a 100)
        if nota < 0 or nota > 100:
            return Response(
                {'error': 'La nota debe estar entre 0 y 100.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Regla de negocio 2: Validar que la evaluación pertenezca al mismo grupo en el que está matriculado el estudiante
        if matricula.grupo_id != evaluacion.grupo_id:
            return Response(
                {
                    'error': (
                        'La evaluación no pertenece al grupo '
                        'de la matrícula seleccionada.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Guarda la calificación si pasa todas las validaciones
        calificacion = serializer.save()

        # Retorna la calificación creada con código HTTP 201 (Creado exitosamente)
        return Response(
            CalificacionSerializer(calificacion).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) una calificación específica por su ID (pk)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_calificacion(request, pk):

    # Busca la calificación con consultas optimizadas, manejando el error 404 si no existe
    try:
        calificacion = Calificacion.objects.select_related(
            'matricula__estudiante',
            'evaluacion',
        ).get(pk=pk)
    except Calificacion.DoesNotExist:
        return Response(
            {'error': 'La calificación no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Manejo de petición GET: retorna el detalle individual de la calificación
    if request.method == 'GET':
        serializer = CalificacionSerializer(calificacion)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Manejo de peticiones PUT o PATCH para actualizar una calificación existente
    if request.method in ['PUT', 'PATCH']:
        serializer = CalificacionSerializer(
            calificacion,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )

        if serializer.is_valid():
            datos = serializer.validated_data

            # Obtiene los datos nuevos o mantiene los valores actuales si no se enviaron en la petición
            matricula = datos.get(
                'matricula',
                calificacion.matricula,
            )

            evaluacion = datos.get(
                'evaluacion',
                calificacion.evaluacion,
            )

            nota = datos.get(
                'nota_obtenida',
                calificacion.nota_obtenida,
            )

            # Validación de rango de nota
            if nota < 0 or nota > 100:
                return Response(
                    {'error': 'La nota debe estar entre 0 y 100.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validación de coherencia entre el grupo de la matrícula y el grupo de la evaluación
            if matricula.grupo_id != evaluacion.grupo_id:
                return Response(
                    {
                        'error': (
                            'La evaluación no pertenece al grupo '
                            'de la matrícula seleccionada.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Manejo de petición DELETE: elimina el registro de la calificación
    calificacion.delete()

    # Retorna respuesta exitosa sin contenido (código HTTP 204)
    return Response(status=status.HTTP_204_NO_CONTENT)
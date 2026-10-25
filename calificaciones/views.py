from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Evaluacion, Calificacion
from .serializers import EvaluacionSerializer, CalificacionSerializer


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_evaluaciones(request):

    if request.method == 'GET':
        evaluaciones = Evaluacion.objects.select_related('grupo').all()

        grupo_id = request.query_params.get('grupo')

        if grupo_id:
            evaluaciones = evaluaciones.filter(grupo_id=grupo_id)

        evaluaciones = evaluaciones.order_by('grupo_id', 'nombre')

        serializer = EvaluacionSerializer(evaluaciones, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = EvaluacionSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_evaluacion(request, pk):

    try:
        evaluacion = Evaluacion.objects.select_related('grupo').get(pk=pk)
    except Evaluacion.DoesNotExist:
        return Response(
            {'error': 'La evaluación no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = EvaluacionSerializer(evaluacion)

        return Response(serializer.data, status=status.HTTP_200_OK)

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

    evaluacion.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_calificaciones(request):

    if request.method == 'GET':
        calificaciones = Calificacion.objects.select_related(
            'matricula__estudiante',
            'evaluacion',
        ).all()

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

        calificaciones = calificaciones.order_by(
            'matricula_id',
            'evaluacion_id',
        )

        serializer = CalificacionSerializer(calificaciones, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = CalificacionSerializer(data=request.data)

    if serializer.is_valid():
        datos = serializer.validated_data

        matricula = datos['matricula']
        evaluacion = datos['evaluacion']
        nota = datos['nota_obtenida']

        if nota < 0 or nota > 100:
            return Response(
                {'error': 'La nota debe estar entre 0 y 100.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

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

        calificacion = serializer.save()

        return Response(
            CalificacionSerializer(calificacion).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_calificacion(request, pk):

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

    if request.method == 'GET':
        serializer = CalificacionSerializer(calificacion)

        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH']:
        serializer = CalificacionSerializer(
            calificacion,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )

        if serializer.is_valid():
            datos = serializer.validated_data

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

            if nota < 0 or nota > 100:
                return Response(
                    {'error': 'La nota debe estar entre 0 y 100.'},
                    status=status.HTTP_400_BAD_REQUEST,
                )

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

    calificacion.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)

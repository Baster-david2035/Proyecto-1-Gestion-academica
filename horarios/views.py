from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import HorarioGrupo
from .serializers import HorarioGrupoSerializer


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_horarios(request):

    if request.method == 'GET':
        horarios = HorarioGrupo.objects.select_related('grupo').all()

        grupo_id = request.query_params.get('grupo')
        dia = request.query_params.get('dia')
        aula = request.query_params.get('aula')

        if grupo_id:
            horarios = horarios.filter(grupo_id=grupo_id)

        if dia:
            horarios = horarios.filter(dia__iexact=dia.upper())

        if aula:
            horarios = horarios.filter(aula__icontains=aula)

        horarios = horarios.order_by('dia', 'hora_inicio')

        serializer = HorarioGrupoSerializer(horarios, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    serializer = HorarioGrupoSerializer(data=request.data)

    if serializer.is_valid():
        datos = serializer.validated_data

        grupo = datos['grupo']
        dia = datos['dia']
        hora_inicio = datos['hora_inicio']
        hora_fin = datos['hora_fin']
        aula = datos['aula']

        if hora_inicio >= hora_fin:
            return Response(
                {
                    'error': (
                        'La hora de inicio debe ser anterior '
                        'a la hora de finalización.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        conflicto_grupo = HorarioGrupo.objects.filter(
            grupo=grupo,
            dia=dia,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        ).exists()

        if conflicto_grupo:
            return Response(
                {
                    'error': (
                        'El grupo ya tiene un horario '
                        'que se superpone con ese intervalo.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        conflicto_aula = HorarioGrupo.objects.filter(
            dia=dia,
            aula__iexact=aula,
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio,
        ).exists()

        if conflicto_aula:
            return Response(
                {
                    'error': (
                        'El aula ya está ocupada durante '
                        'ese intervalo.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        horario = serializer.save()

        return Response(
            HorarioGrupoSerializer(horario).data,
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_horario(request, pk):

    try:
        horario = HorarioGrupo.objects.select_related('grupo').get(pk=pk)
    except HorarioGrupo.DoesNotExist:
        return Response(
            {'error': 'El horario no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == 'GET':
        serializer = HorarioGrupoSerializer(horario)

        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method in ['PUT', 'PATCH']:
        serializer = HorarioGrupoSerializer(
            horario,
            data=request.data,
            partial=(request.method == 'PATCH'),
        )

        if serializer.is_valid():
            datos = serializer.validated_data

            grupo = datos.get('grupo', horario.grupo)
            dia = datos.get('dia', horario.dia)
            hora_inicio = datos.get(
                'hora_inicio',
                horario.hora_inicio,
            )
            hora_fin = datos.get(
                'hora_fin',
                horario.hora_fin,
            )
            aula = datos.get('aula', horario.aula)

            if hora_inicio >= hora_fin:
                return Response(
                    {
                        'error': (
                            'La hora de inicio debe ser anterior '
                            'a la hora de finalización.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            conflicto_grupo = HorarioGrupo.objects.filter(
                grupo=grupo,
                dia=dia,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            ).exclude(pk=horario.pk).exists()

            if conflicto_grupo:
                return Response(
                    {
                        'error': (
                            'El grupo ya tiene un horario '
                            'que se superpone con ese intervalo.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            conflicto_aula = HorarioGrupo.objects.filter(
                dia=dia,
                aula__iexact=aula,
                hora_inicio__lt=hora_fin,
                hora_fin__gt=hora_inicio,
            ).exclude(pk=horario.pk).exists()

            if conflicto_aula:
                return Response(
                    {
                        'error': (
                            'El aula ya está ocupada durante '
                            'ese intervalo.'
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

    horario.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)
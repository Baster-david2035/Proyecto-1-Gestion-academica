from rest_framework import status
from rest_framework.decorators import (api_view,authentication_classes,permission_classes)
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import HorarioGrupo
from .serializers import HorarioGrupoSerializer


# Vista de API basada en funciones para listar (GET) y crear (POST) horarios de grupos
@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])  # Requiere autenticación mediante token de acceso
@permission_classes([IsAuthenticated])         # Exige que el usuario haya iniciado sesión obligatoriamente
def listar_crear_horarios(request):

    # Manejo de peticiones GET: listar y filtrar los horarios registrados
    if request.method == 'GET':
        # Obtiene todos los horarios optimizando la consulta a la base de datos con select_related para traer el grupo asociado
        horarios = HorarioGrupo.objects.select_related('grupo').all()

        # Captura los parámetros opcionales enviados en la URL (?grupo=X&dia=LUN&aula=Lab-01)
        grupo_id = request.query_params.get('grupo')
        dia = request.query_params.get('dia')
        aula = request.query_params.get('aula')

        # Aplica filtro por ID de grupo si fue especificado
        if grupo_id:
            horarios = horarios.filter(grupo_id=grupo_id)

        # Aplica filtro por día de la semana si fue especificado (convertido a mayúsculas)
        if dia:
            horarios = horarios.filter(dia__iexact=dia.upper())

        # Aplica filtro por nombre o coincidencia parcial de aula si fue especificado
        if aula:
            horarios = horarios.filter(aula__icontains=aula)

        # Ordena los resultados cronológicamente por día y hora de inicio
        horarios = horarios.order_by('dia', 'hora_inicio')

        # Serializa el queryset resultante en formato JSON
        serializer = HorarioGrupoSerializer(horarios, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    # Manejo de peticiones POST: creación de un nuevo horario
    serializer = HorarioGrupoSerializer(data=request.data)

    if serializer.is_valid():
        datos = serializer.validated_data

        # Extrae los datos validados para realizar las validaciones de negocio personalizadas
        grupo = datos['grupo']
        dia = datos['dia']
        hora_inicio = datos['hora_inicio']
        hora_fin = datos['hora_fin']
        aula = datos['aula']

        # Regla de negocio 1: La hora de inicio debe ser estrictamente anterior a la hora de finalización
        if hora_inicio >= hora_fin:
            return Response(
                {
                    'error': (
                        'La hora de inicio debe ser anterior '
                        'a la hora de finalización.'
                    )
                },status=status.HTTP_400_BAD_REQUEST)

        # Regla de negocio 2: Validar que el mismo grupo no tenga otro horario que se encape o superponga en el mismo día y hora
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
                },status=status.HTTP_400_BAD_REQUEST)

        # Regla de negocio 3: Validar que el aula no esté ocupada por otro grupo en el mismo día y intervalo de horas
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
                },status=status.HTTP_400_BAD_REQUEST)

        # Si pasa todas las validaciones, guarda el nuevo horario en la base de datos
        horario = serializer.save()

        # Retorna el objeto creado con código HTTP 201 (Creado exitosamente)
        return Response(HorarioGrupoSerializer(horario).data,status=status.HTTP_201_CREATED)
    # Si los datos base del serializer no son válidos, retorna los errores con código HTTP 400
    return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

# Vista de API para consultar (GET), actualizar (PUT/PATCH) o eliminar (DELETE) un horario específico por su ID (pk)
@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])  # Requiere autenticación por token
@permission_classes([IsAuthenticated])         # Exige sesión activa
def detalle_horario(request, pk):
    # Intenta buscar el horario por su ID, manejando la excepción si no existe (retorna HTTP 404)
    try:
        horario = HorarioGrupo.objects.select_related('grupo').get(pk=pk)
    except HorarioGrupo.DoesNotExist:
        return Response(
            {'error': 'El horario no existe.'},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Manejo de petición GET: retorna el detalle completo de ese horario individual
    if request.method == 'GET':
        serializer = HorarioGrupoSerializer(horario)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Manejo de peticiones PUT (reemplazo completo) o PATCH (actualización parcial)
    if request.method in ['PUT', 'PATCH']:
        serializer = HorarioGrupoSerializer(
            horario,
            data=request.data,
            partial=(request.method == 'PATCH'),  # Permite enviar solo algunos campos si es PATCH
        )

        if serializer.is_valid():
            datos = serializer.validated_data

            # Obtiene los valores nuevos o mantiene los actuales si no se enviaron en la petición
            grupo = datos.get('grupo', horario.grupo)
            dia = datos.get('dia', horario.dia)
            hora_inicio = datos.get('hora_inicio',horario.hora_inicio)
            hora_fin = datos.get('hora_fin',horario.hora_fin)
            aula = datos.get('aula', horario.aula)

            # Validación de coherencia en las horas
            if hora_inicio >= hora_fin:
                return Response(
                    {
                        'error': (
                            'La hora de inicio debe ser anterior '
                            'a la hora de finalización.'
                        )
                    },status=status.HTTP_400_BAD_REQUEST)
            # Valida conflictos de superposición para el grupo (excluyendo el registro actual mediante .exclude(pk=horario.pk))
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
                    },status=status.HTTP_400_BAD_REQUEST)
            # Valida conflictos de superposición de aula (excluyendo el registro actual)
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
                    },status=status.HTTP_400_BAD_REQUEST)

            # Guarda los cambios actualizados
            serializer.save()

            return Response(serializer.data,status=status.HTTP_200_OK)

        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

    # Manejo de petición DELETE: elimina el registro del horario de la base de datos
    horario.delete()

    # Retorna una respuesta exitosa sin contenido (código HTTP 204)
    return Response(status=status.HTTP_204_NO_CONTENT)
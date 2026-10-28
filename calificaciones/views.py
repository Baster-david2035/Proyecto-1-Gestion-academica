from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.views import es_administrador, obtener_rol
from matricula.models import Matricula
from .models import Calificacion, Evaluacion
from .serializers import CalificacionSerializer, EvaluacionSerializer


def _grupos_visibles(usuario):
    from academico.models import Grupo

    grupos = Grupo.objects.all()
    if es_administrador(usuario):
        return grupos
    rol = obtener_rol(usuario)
    if rol == 'PROFESOR':
        return grupos.filter(profesor=usuario)
    if rol == 'ESTUDIANTE':
        return grupos.filter(matricula__estudiante=usuario).distinct()
    return grupos.none()


def _puede_editar_grupo(usuario, grupo):
    return es_administrador(usuario) or (
        obtener_rol(usuario) == 'PROFESOR' and grupo.profesor_id == usuario.pk
    )


def _queryset_evaluaciones(usuario):
    return Evaluacion.objects.select_related('grupo').filter(
        grupo__in=_grupos_visibles(usuario)
    )


def _queryset_calificaciones(usuario):
    registros = Calificacion.objects.select_related(
        'matricula__estudiante', 'matricula__grupo', 'evaluacion__grupo'
    )
    if es_administrador(usuario):
        return registros
    rol = obtener_rol(usuario)
    if rol == 'PROFESOR':
        return registros.filter(evaluacion__grupo__profesor=usuario)
    if rol == 'ESTUDIANTE':
        return registros.filter(matricula__estudiante=usuario)
    return registros.none()


def _paginada(request, queryset, serializer_class):
    try:
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 10)), 50)
        if page < 1 or page_size < 1:
            raise ValueError
    except (TypeError, ValueError):
        return Response(
            {'error': 'page y page_size deben ser enteros positivos.'},
            status=status.HTTP_400_BAD_REQUEST,
        )
    total = queryset.count()
    items = queryset[(page - 1) * page_size:page * page_size]
    return Response({
        'count': total,
        'page': page,
        'page_size': page_size,
        'results': serializer_class(items, many=True).data,
    })


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_evaluaciones(request):
    if request.method == 'GET':
        queryset = _queryset_evaluaciones(request.user).order_by('grupo_id', 'nombre')
        grupo_id = request.query_params.get('grupo')
        if grupo_id:
            try:
                if int(grupo_id) < 1:
                    raise ValueError
            except (TypeError, ValueError):
                return Response({'error': 'grupo debe ser un entero positivo.'}, status=400)
            queryset = queryset.filter(grupo_id=grupo_id)
        return _paginada(request, queryset, EvaluacionSerializer)

    serializer = EvaluacionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    grupo = serializer.validated_data['grupo']
    if not _puede_editar_grupo(request.user, grupo):
        return Response({'error': 'Solo el administrador o profesor del grupo puede gestionar evaluaciones.'}, status=403)
    with transaction.atomic():
        # Serializar el total por grupo para evitar que dos altas simultáneas
        # excedan el 100% en MySQL.
        from academico.models import Grupo
        Grupo.objects.select_for_update().get(pk=grupo.pk)
        serializer = EvaluacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        evaluacion = serializer.save()
    return Response(EvaluacionSerializer(evaluacion).data, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_evaluacion(request, pk):
    evaluacion = get_object_or_404(_queryset_evaluaciones(request.user), pk=pk)
    if request.method == 'GET':
        return Response(EvaluacionSerializer(evaluacion).data)
    if not _puede_editar_grupo(request.user, evaluacion.grupo):
        return Response({'error': 'Solo el administrador o profesor del grupo puede modificar evaluaciones.'}, status=403)
    if request.method in ('PUT', 'PATCH'):
        serializer = EvaluacionSerializer(
            evaluacion,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if not _puede_editar_grupo(request.user, serializer.validated_data.get('grupo', evaluacion.grupo)):
            return Response({'error': 'No puede trasladar la evaluación a un grupo que no imparte.'}, status=403)
        with transaction.atomic():
            from academico.models import Grupo
            group_id = serializer.validated_data.get('grupo', evaluacion.grupo).pk
            Grupo.objects.select_for_update().get(pk=group_id)
            serializer = EvaluacionSerializer(evaluacion, data=request.data, partial=request.method == 'PATCH')
            serializer.is_valid(raise_exception=True)
            serializer.save()
        return Response(serializer.data)
    evaluacion.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def validar_porcentajes_grupo(request, grupo_id):
    if not _grupos_visibles(request.user).filter(pk=grupo_id).exists():
        return Response({'error': 'El grupo no existe o no está disponible para este usuario.'}, status=404)
    queryset = Evaluacion.objects.filter(grupo_id=grupo_id)
    total = sum(queryset.values_list('porcentaje', flat=True), Decimal('0.00'))
    return Response({
        'valido': total == Decimal('100.00'),
        'grupo_id': grupo_id,
        'porcentaje_acumulado': str(total),
        'porcentaje_faltante': str(max(Decimal('0.00'), Decimal('100.00') - total)),
        'porcentaje_excedido': str(max(Decimal('0.00'), total - Decimal('100.00'))),
    })


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_calificaciones(request):
    if request.method == 'GET':
        queryset = _queryset_calificaciones(request.user).order_by('matricula_id', 'evaluacion_id')
        for param, field in (('matricula', 'matricula_id'), ('evaluacion', 'evaluacion_id')):
            value = request.query_params.get(param)
            if value:
                try:
                    if int(value) < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    return Response({'error': f'{param} debe ser un entero positivo.'}, status=400)
                queryset = queryset.filter(**{field: value})
        return _paginada(request, queryset, CalificacionSerializer)

    serializer = CalificacionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    evaluacion = serializer.validated_data['evaluacion']
    if not _puede_editar_grupo(request.user, evaluacion.grupo):
        return Response({'error': 'Solo el administrador o profesor del grupo puede registrar notas.'}, status=403)
    with transaction.atomic():
        Matricula.objects.select_for_update().get(
            pk=serializer.validated_data['matricula'].pk
        )
        serializer = CalificacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        calificacion = serializer.save()
    return Response(CalificacionSerializer(calificacion).data, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_calificacion(request, pk):
    calificacion = get_object_or_404(_queryset_calificaciones(request.user), pk=pk)
    if request.method == 'GET':
        return Response(CalificacionSerializer(calificacion).data)
    if not _puede_editar_grupo(request.user, calificacion.evaluacion.grupo):
        return Response({'error': 'Solo el administrador o profesor del grupo puede modificar notas.'}, status=403)
    if request.method in ('PUT', 'PATCH'):
        serializer = CalificacionSerializer(
            calificacion,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        if not _puede_editar_grupo(request.user, serializer.validated_data.get('evaluacion', calificacion.evaluacion).grupo):
            return Response({'error': 'No puede mover la nota a un grupo que no imparte.'}, status=403)
        matricula_id = serializer.validated_data.get(
            'matricula', calificacion.matricula
        ).pk
        with transaction.atomic():
            Matricula.objects.select_for_update().get(pk=matricula_id)
            serializer = CalificacionSerializer(
                calificacion,
                data=request.data,
                partial=request.method == 'PATCH',
            )
            serializer.is_valid(raise_exception=True)
            if not _puede_editar_grupo(
                request.user,
                serializer.validated_data.get(
                    'evaluacion', calificacion.evaluacion
                ).grupo,
            ):
                return Response(
                    {'error': 'No puede mover la nota a un grupo que no imparte.'},
                    status=403,
                )
            serializer.save()
        return Response(serializer.data)
    calificacion.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

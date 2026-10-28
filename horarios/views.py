from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from usuarios.views import es_administrador, obtener_rol
from .models import HorarioGrupo
from .serializers import HorarioGrupoSerializer


def _horarios_visibles(usuario):
    queryset = HorarioGrupo.objects.select_related('grupo', 'grupo__curso', 'grupo__periodo')
    if es_administrador(usuario):
        return queryset
    rol = obtener_rol(usuario)
    if rol == 'PROFESOR':
        return queryset.filter(grupo__profesor=usuario)
    if rol == 'ESTUDIANTE':
        return queryset.filter(
            grupo__matricula__estudiante=usuario,
            grupo__matricula__estado='MATRICULADO',
        ).distinct()
    return queryset.none()


def _puede_editar(usuario, grupo):
    return es_administrador(usuario) or (
        obtener_rol(usuario) == 'PROFESOR' and grupo.profesor_id == usuario.pk
    )


def _pagina(request, queryset):
    try:
        page = int(request.query_params.get('page', 1))
        page_size = min(int(request.query_params.get('page_size', 10)), 50)
        if page < 1 or page_size < 1:
            raise ValueError
    except (TypeError, ValueError):
        return Response({'error': 'page y page_size deben ser enteros positivos.'}, status=400)
    total = queryset.count()
    rows = queryset[(page - 1) * page_size:page * page_size]
    return Response({
        'count': total,
        'page': page,
        'page_size': page_size,
        'results': HorarioGrupoSerializer(rows, many=True).data,
    })


@api_view(['GET', 'POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def listar_crear_horarios(request):
    if request.method == 'GET':
        queryset = _horarios_visibles(request.user)
        grupo = request.query_params.get('grupo')
        dia = request.query_params.get('dia')
        aula = request.query_params.get('aula')
        if grupo:
            try:
                if int(grupo) < 1:
                    raise ValueError
            except (TypeError, ValueError):
                return Response({'error': 'grupo debe ser un entero positivo.'}, status=400)
            queryset = queryset.filter(grupo_id=grupo)
        if dia:
            queryset = queryset.filter(dia__iexact=dia.upper())
        if aula:
            queryset = queryset.filter(aula__icontains=aula)
        return _pagina(request, queryset.order_by('dia', 'hora_inicio'))

    serializer = HorarioGrupoSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)
    grupo = serializer.validated_data['grupo']
    if not _puede_editar(request.user, grupo):
        return Response({'error': 'Solo el administrador o profesor asignado puede gestionar este horario.'}, status=403)
    horario = serializer.save()
    return Response(HorarioGrupoSerializer(horario).data, status=201)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def detalle_horario(request, pk):
    horario = get_object_or_404(_horarios_visibles(request.user), pk=pk)
    if request.method == 'GET':
        return Response(HorarioGrupoSerializer(horario).data)
    if not _puede_editar(request.user, horario.grupo):
        return Response({'error': 'Solo el administrador o profesor asignado puede modificar este horario.'}, status=403)
    if request.method in ('PUT', 'PATCH'):
        serializer = HorarioGrupoSerializer(
            horario,
            data=request.data,
            partial=request.method == 'PATCH',
        )
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)
        grupo_nuevo = serializer.validated_data.get('grupo', horario.grupo)
        if not _puede_editar(request.user, grupo_nuevo):
            return Response({'error': 'No puede mover el horario a un grupo que no imparte.'}, status=403)
        serializer.save()
        return Response(serializer.data)
    horario.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

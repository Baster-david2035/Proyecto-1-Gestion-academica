from rest_framework import serializers
from .models import Carrera, Curso, PeriodoLectivo, Grupo


class CarreraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Carrera
        fields = ['id', 'codigo', 'nombre', 'descripcion']


class CursoSerializer(serializers.ModelSerializer):
    carrera_nombre = serializers.ReadOnlyField(source='carrera.nombre')

    class Meta:
        model = Curso
        fields = [
            'id',
            'codigo',
            'nombre',
            'creditos',
            'carrera',
            'carrera_nombre',
            'prerrequisitos',
        ]


class PeriodoLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoLectivo
        fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin', 'activo']


class GrupoSerializer(serializers.ModelSerializer):
    curso_nombre = serializers.ReadOnlyField(source='curso.nombre')
    periodo_nombre = serializers.ReadOnlyField(source='periodo.nombre')
    profesor_nombre = serializers.ReadOnlyField(
        source='profesor.get_full_name'
    )

    class Meta:
        model = Grupo
        fields = ['id',
            'curso',
            'curso_nombre',
            'periodo',
            'periodo_nombre',
            'numero_grupo',
            'profesor',
            'profesor_nombre',
            'cupo_maximo',]
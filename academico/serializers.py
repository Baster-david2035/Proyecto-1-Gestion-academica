from rest_framework import serializers
from .models import Carrera, Curso, PeriodoLectivo, Grupo


# Serializer para transformar el modelo Carrera en formato JSON (y viceversa)
class CarreraSerializer(serializers.ModelSerializer):

    class Meta:
        model = Carrera
        fields = ['id', 'codigo', 'nombre', 'descripcion']

    def validate_codigo(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "El código de la carrera es obligatorio."
            )

        return value

    def validate_nombre(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El nombre de la carrera es obligatorio."
            )

        return value

    def validate_descripcion(self, value):
        if value is not None:
            value = value.strip()

        return value



# Serializer para transformar el modelo Curso en formato JSON (y viceversa)
class CursoSerializer(serializers.ModelSerializer):
    
    # Campo de solo lectura para exponer el nombre de la carrera asociada 
    # navegando a través de la relación: carrera -> nombre.
    carrera_nombre = serializers.ReadOnlyField(source='carrera.nombre')

    class Meta:
        model = Curso
        # Lista de campos expuestos por la API para los cursos (incluyendo prerrequisitos y relación con carrera)
        fields = [
            'id',
            'codigo',
            'nombre',
            'creditos',
            'carrera',
            'carrera_nombre',
            'prerrequisitos',
        ]


# Serializer para transformar el modelo PeriodoLectivo en formato JSON (y viceversa)
class PeriodoLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoLectivo
        # Lista de campos expuestos para la gestión de periodos o ciclos lectivos
        fields = ['id', 'nombre', 'fecha_inicio', 'fecha_fin', 'activo']


# Serializer para transformar el modelo Grupo en formato JSON (y viceversa)
class GrupoSerializer(serializers.ModelSerializer):
    
    # Campo de solo lectura para exponer el nombre del curso asociado
    curso_nombre = serializers.ReadOnlyField(source='curso.nombre')
    
    # Campo de solo lectura para exponer el nombre del periodo lectivo asociado
    periodo_nombre = serializers.ReadOnlyField(source='periodo.nombre')
    
    # Campo de solo lectura para obtener el nombre completo del profesor asignado 
    # a través de la relación: profesor -> get_full_name().
    profesor_nombre = serializers.ReadOnlyField(
        source='profesor.get_full_name'
    )

    class Meta:
        model = Grupo
        # Lista de campos expuestos por la API para la gestión de grupos académicos
        fields = ['id',
            'curso',
            'curso_nombre',
            'periodo',
            'periodo_nombre',
            'numero_grupo',
            'profesor',
            'profesor_nombre',
            'cupo_maximo',]
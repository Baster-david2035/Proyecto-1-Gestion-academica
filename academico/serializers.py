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
    
    carrera_nombre = serializers.ReadOnlyField(
        source='carrera.nombre'
    )

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

    def validate_codigo(self, value):
        value = value.strip().upper()

        if not value:
            raise serializers.ValidationError(
                "El código del curso es obligatorio."
            )

        return value

    def validate_nombre(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El nombre del curso es obligatorio."
            )

        return value

    def validate_creditos(self, value):
        if value <= 0:
            raise serializers.ValidationError(
                "El curso debe tener al menos un crédito."
            )

        return value

    def validate(self, data):
        prerrequisitos = data.get(
            'prerrequisitos',
            self.instance.prerrequisitos.all()
            if self.instance else []
        )

        # Un curso no puede ser su propio prerrequisito.
        if self.instance and self.instance in prerrequisitos:
            raise serializers.ValidationError({
                'prerrequisitos':
                    "Un curso no puede ser su propio prerrequisito."
            })

        return data


# Serializer para transformar el modelo PeriodoLectivo en formato JSON (y viceversa)
class PeriodoLectivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PeriodoLectivo
        fields = [
            'id',
            'nombre',
            'fecha_inicio',
            'fecha_fin',
            'activo',
        ]

    def validate_nombre(self, value):
        value = value.strip()

        if not value:
            raise serializers.ValidationError(
                "El nombre del periodo es obligatorio."
            )

        return value

    def validate(self, data):
        fecha_inicio = data.get(
            'fecha_inicio',
            self.instance.fecha_inicio
            if self.instance else None
        )

        fecha_fin = data.get(
            'fecha_fin',
            self.instance.fecha_fin
            if self.instance else None
        )

        if (
            fecha_inicio is not None
            and fecha_fin is not None
            and fecha_fin < fecha_inicio
        ):
            raise serializers.ValidationError({
                'fecha_fin':
                    "La fecha de finalización no puede ser "
                    "anterior a la fecha de inicio."
            })

        return data



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
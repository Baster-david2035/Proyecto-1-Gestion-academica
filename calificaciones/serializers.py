from rest_framework import serializers
from .models import Evaluacion, Calificacion


# Serializer para transformar el modelo Evaluacion en formato JSON (y viceversa)
class EvaluacionSerializer(serializers.ModelSerializer):
    
    grupo_detalle = serializers.ReadOnlyField(
    source='grupo.__str__'
)

class Meta:
    model = Evaluacion
    fields = [
        'id',
        'grupo',
        'grupo_detalle',
        'nombre',
        'porcentaje',
    ]

def validate_nombre(self, nombre):
    nombre = nombre.strip()

    if not nombre:
        raise serializers.ValidationError(
            'El nombre de la evaluación no puede estar vacío.'
        )

    return nombre

def validate_porcentaje(self, porcentaje):
    if porcentaje <= 0 or porcentaje > 100:
        raise serializers.ValidationError(
            'El porcentaje debe ser mayor que 0 y menor o igual a 100.'
        )

    return porcentaje


# Serializer para transformar el modelo Calificacion en formato JSON (y viceversa)
class CalificacionSerializer(serializers.ModelSerializer):
    
   estudiante_nombre = serializers.ReadOnlyField(
    source='matricula.estudiante.get_full_name'
)

evaluacion_nombre = serializers.ReadOnlyField(
    source='evaluacion.nombre'
)

class Meta:
    model = Calificacion
    fields = [
        'id',
        'matricula',
        'estudiante_nombre',
        'evaluacion',
        'evaluacion_nombre',
        'nota_obtenida',
    ]

def validate_nota_obtenida(self, nota):
    if nota < 0 or nota > 100:
        raise serializers.ValidationError(
            'La nota debe estar entre 0 y 100.'
        )

    return nota

def validate(self, attrs):
    matricula = attrs.get(
        'matricula',
        getattr(self.instance, 'matricula', None)
    )

    evaluacion = attrs.get(
        'evaluacion',
        getattr(self.instance, 'evaluacion', None)
    )

    if matricula is not None and evaluacion is not None:

        # La matrícula y la evaluación deben pertenecer al mismo grupo.
        if matricula.grupo_id != evaluacion.grupo_id:
            raise serializers.ValidationError({
                'evaluacion': (
                    'La evaluación debe pertenecer al grupo '
                    'en el que está matriculado el estudiante.'
                )
            })

        # No permitir calificar a un estudiante retirado.
        if matricula.estado != 'MATRICULADO':
            raise serializers.ValidationError({
                'matricula': (
                    'No se pueden registrar calificaciones '
                    'para una matrícula retirada.'
                )
            })

        # Evitar calificaciones duplicadas.
        calificaciones = Calificacion.objects.filter(
            matricula=matricula,
            evaluacion=evaluacion
        )

        # Excluir el registro actual cuando se está actualizando.
        if self.instance is not None:
            calificaciones = calificaciones.exclude(
                pk=self.instance.pk
            )

        if calificaciones.exists():
            raise serializers.ValidationError({
                'evaluacion': (
                    'Esta matrícula ya tiene una calificación '
                    'registrada para esa evaluación.'
                )
            })

    return attrs
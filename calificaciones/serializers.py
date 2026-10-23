from rest_framework import serializers
from .models import Evaluacion, Calificacion


class EvaluacionSerializer(serializers.ModelSerializer):
    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = Evaluacion
        fields = ['id', 'grupo', 'grupo_detalle', 'nombre', 'porcentaje']


class CalificacionSerializer(serializers.ModelSerializer):
    estudiante_nombre = serializers.ReadOnlyField(source='matricula.estudiante.get_full_name')
    evaluacion_nombre = serializers.ReadOnlyField(source='evaluacion.nombre')

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
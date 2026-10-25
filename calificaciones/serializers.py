from rest_framework import serializers
from .models import Evaluacion, Calificacion


# Serializer para transformar el modelo Evaluacion en formato JSON (y viceversa)
class EvaluacionSerializer(serializers.ModelSerializer):
    
    # Campo de solo lectura para exponer la representación en texto del grupo asociado 
    # utilizando el método __str__ del modelo Grupo.
    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = Evaluacion
        # Lista de campos que se incluirán al serializar o deserializar las evaluaciones en la API
        fields = ['id', 'grupo', 'grupo_detalle', 'nombre', 'porcentaje']


# Serializer para transformar el modelo Calificacion en formato JSON (y viceversa)
class CalificacionSerializer(serializers.ModelSerializer):
    
    # Campo de solo lectura para obtener el nombre completo del estudiante relacionado 
    # navegando a través de la relación: matricula -> estudiante -> get_full_name().
    estudiante_nombre = serializers.ReadOnlyField(source='matricula.estudiante.get_full_name')
    
    # Campo de solo lectura para exponer el nombre de la evaluación asociada 
    # navegando a través de la relación: evaluacion -> nombre.
    evaluacion_nombre = serializers.ReadOnlyField(source='evaluacion.nombre')

    class Meta:
        model = Calificacion
        # Lista de campos expuestos por la API para la gestión de calificaciones
        fields = [
            'id',
            'matricula',
            'estudiante_nombre',
            'evaluacion',
            'evaluacion_nombre',
            'nota_obtenida',
        ]
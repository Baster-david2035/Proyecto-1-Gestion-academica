from rest_framework import serializers
from .models import HorarioGrupo


# Serializer para transformar el modelo HorarioGrupo en formato JSON (y viceversa)
class HorarioGrupoSerializer(serializers.ModelSerializer):
    
    # Campo de solo lectura para exponer la representación en texto del grupo asociado 
    # utilizando el método __str__ definido en el modelo Grupo.
    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = HorarioGrupo
        # Lista de campos que se incluirán al serializar o deserializar los datos en la API
        fields = [
            'id',
            'grupo',
            'grupo_detalle',
            'dia',
            'hora_inicio',
            'hora_fin',
            'aula',
        ]
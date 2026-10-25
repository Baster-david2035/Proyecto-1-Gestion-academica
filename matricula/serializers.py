from rest_framework import serializers
from .models import Matricula


# Serializer para transformar el modelo Matricula en JSON (y viceversa).
class MatriculaSerializer(serializers.ModelSerializer):
    
    # Campo de solo lectura para exponer el nombre de usuario (username) del estudiante asociado.
    # 'source="estudiante.username"' indica que el valor se obtiene navegando desde la relación 'estudiante' hacia su atributo 'username'.
    estudiante_username = serializers.ReadOnlyField(source='estudiante.username')
    
    # Campo de solo lectura para exponer la representación en texto del grupo (__str__ del modelo Grupo).
    # 'source="grupo.__str__"' toma el resultado del método __str__ del objeto grupo relacionado.
    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = Matricula
        # Lista de campos que se incluirán en la serialización y deserialización de la API
        fields = [
            'id',
            'estudiante',
            'estudiante_username',
            'grupo',
            'grupo_detalle',
            'fecha_matricula',
            'estado',
        ]
        # Campos que solo se pueden leer desde la API y no pueden ser modificados o enviados por el cliente en POST/PUT/PATCH
        read_only_fields = ['fecha_matricula']
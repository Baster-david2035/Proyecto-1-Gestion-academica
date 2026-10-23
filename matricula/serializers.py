from rest_framework import serializers
from .models import Matricula


class MatriculaSerializer(serializers.ModelSerializer):
    estudiante_username = serializers.ReadOnlyField(source='estudiante.username')
    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = Matricula
        fields = [
            'id',
            'estudiante',
            'estudiante_username',
            'grupo',
            'grupo_detalle',
            'fecha_matricula',
            'estado',
        ]
        read_only_fields = ['fecha_matricula']
from rest_framework import serializers
from .models import HorarioGrupo


class HorarioGrupoSerializer(serializers.ModelSerializer):
    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = HorarioGrupo
        fields = [
            'id',
            'grupo',
            'grupo_detalle',
            'dia',
            'hora_inicio',
            'hora_fin',
            'aula',
        ]
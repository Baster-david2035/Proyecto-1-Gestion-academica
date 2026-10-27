from rest_framework import serializers
from .models import HorarioGrupo


grupo_detalle = serializers.ReadOnlyField(
    source='grupo.__str__'
)

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

def validate_aula(self, aula):
    aula = aula.strip()

    if not aula:
        raise serializers.ValidationError(
            'El aula no puede estar vacía.'
        )

    return aula

def validate(self, attrs):
    grupo = attrs.get(
        'grupo',
        getattr(self.instance, 'grupo', None)
    )

    dia = attrs.get(
        'dia',
        getattr(self.instance, 'dia', None)
    )

    hora_inicio = attrs.get(
        'hora_inicio',
        getattr(self.instance, 'hora_inicio', None)
    )

    hora_fin = attrs.get(
        'hora_fin',
        getattr(self.instance, 'hora_fin', None)
    )

    aula = attrs.get(
        'aula',
        getattr(self.instance, 'aula', None)
    )

    # La hora final debe ser posterior a la inicial.
    if (
        hora_inicio is not None
        and hora_fin is not None
        and hora_fin <= hora_inicio
    ):
        raise serializers.ValidationError({
            'hora_fin': (
                'La hora de finalización debe ser posterior '
                'a la hora de inicio.'
            )
        })

    if all(
        valor is not None
        for valor in [grupo, dia, hora_inicio, hora_fin, aula]
    ):
        # Buscar horarios del mismo día.
        horarios = HorarioGrupo.objects.filter(dia=dia)

        # Excluir el registro actual cuando se actualiza.
        if self.instance is not None:
            horarios = horarios.exclude(pk=self.instance.pk)

        # Detectar horarios que se solapen.
        horarios_solapados = horarios.filter(
            hora_inicio__lt=hora_fin,
            hora_fin__gt=hora_inicio
        )

        # El mismo grupo no puede tener dos horarios simultáneos.
        if horarios_solapados.filter(grupo=grupo).exists():
            raise serializers.ValidationError({
                'hora_inicio': (
                    'El grupo ya tiene otro horario que se '
                    'solapa en ese día.'
                )
            })

        # Una misma aula no puede asignarse a dos clases simultáneas.
        if horarios_solapados.filter(aula__iexact=aula).exists():
            raise serializers.ValidationError({
                'aula': (
                    'El aula ya está ocupada por otro horario '
                    'durante ese intervalo.'
                )
            })

    return attrs
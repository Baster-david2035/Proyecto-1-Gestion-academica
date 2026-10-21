from django.db import models
from academico.models import Grupo

class HorarioGrupo(models.Model):
    DIAS_SEMANA = (
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
    )
    grupo = models.ForeignKey(
        Grupo, on_delete=models.CASCADE, related_name='horarios'
    )
    dia = models.CharField(max_length=3, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    aula = models.CharField(max_length=20)  # Ej: Lab-01, Aula 104

    def __str__(self):
        return (
            f'{self.grupo} | {self.dia} {self.hora_inicio}-{self.hora_fin}'
            f' ({self.aula})'
        )
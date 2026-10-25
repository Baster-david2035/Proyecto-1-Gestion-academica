from django.db import models
from academico.models import Grupo

# Definición del modelo HorarioGrupo para registrar los días, horas y aulas en que se imparte cada grupo
class HorarioGrupo(models.Model):
    
    # Tupla de opciones para los días de la semana permitidos en el sistema.
    # El primer valor se guarda en la base de datos (ej: 'LUN'), y el segundo es la etiqueta legible.
    DIAS_SEMANA = (
        ('LUN', 'Lunes'),
        ('MAR', 'Martes'),
        ('MIE', 'Miércoles'),
        ('JUE', 'Jueves'),
        ('VIE', 'Viernes'),
        ('SAB', 'Sábado'),
    )
    
    # Relación de muchos a uno (ForeignKey) con el modelo Grupo (proveniente de la app 'academico').
    # on_delete=models.CASCADE elimina los horarios si se borra el grupo asociado.
    # related_name='horarios' permite acceder a todos los horarios de un grupo desde la instancia del grupo (ej: grupo.horarios.all()).
    grupo = models.ForeignKey(
        Grupo, on_delete=models.CASCADE, related_name='horarios'
    )
    # Campo de texto corto para almacenar el día de la semana, limitado a 3 caracteres y restringido a las opciones de DIAS_SEMANA.
    dia = models.CharField(max_length=3, choices=DIAS_SEMANA)
    # Campo de tipo hora (TimeField) para registrar la hora de inicio de la clase.
    hora_inicio = models.TimeField()
    # Campo de tipo hora (TimeField) para registrar la hora de finalización de la clase.
    hora_fin = models.TimeField()
    # Campo de texto para almacenar el nombre o número del aula o laboratorio (Ej: Lab-01, Aula 104).
    aula = models.CharField(max_length=20)
    # Método especial para definir la representación en texto del objeto (por ejemplo, en el panel de administración o logs)
    def __str__(self):
        # Devuelve una cadena combinando el grupo, el día, el rango de horas y el aula entre paréntesis
        return (
            f'{self.grupo} | {self.dia} {self.hora_inicio}-{self.hora_fin}'
            f' ({self.aula})'
        )
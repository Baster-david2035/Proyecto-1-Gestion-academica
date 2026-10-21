from django.db import models
from academico.models import Grupo
from matricula.models import Matricula

class Evaluacion(models.Model):
    grupo = models.ForeignKey(
        Grupo, on_delete=models.CASCADE, related_name='evaluaciones'
    )
    nombre = models.CharField(max_length=50)  # Ej: Examen 1, Tarea 2
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)  # Ej: 30.00

    def __str__(self):
        return f'{self.nombre} ({self.grupo})'


class Calificacion(models.Model):
    matricula = models.ForeignKey(
        Matricula, on_delete=models.CASCADE, related_name='calificaciones'
    )
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    nota_obtenida = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return (
            f'{self.matricula.estudiante.username}: {self.evaluacion.nombre} ='
            f' {self.nota_obtenida}'
        )

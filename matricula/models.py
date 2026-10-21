from django.db import models
from django.contrib.auth.models import User
from academico.models import Grupo

class Matricula(models.Model):
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'perfilusuario__rol': 'ESTUDIANTE'},
    )
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    fecha_matricula = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=20,
        choices=[
            ('MATRICULADO', 'Matriculado'),
            ('RETIRADO', 'Retirado'),
        ],
        default='MATRICULADO',
    )

    class Meta:
        unique_together = ('estudiante', 'grupo')

    def __str__(self):
        return f'{self.estudiante.username} -> {self.grupo}'

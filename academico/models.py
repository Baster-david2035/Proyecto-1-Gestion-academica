from django.db import models
from django.contrib.auth.models import User

class Carrera(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    creditos = models.PositiveIntegerField()
    carrera = models.ForeignKey(
        Carrera, on_delete=models.CASCADE, related_name='cursos'
    )
    prerrequisitos = models.ManyToManyField('self', blank=True, symmetrical=False)

    def __str__(self):
        return f'{self.codigo} - {self.nombre}'

class PeriodoLectivo(models.Model):
    nombre = models.CharField(
        max_length=50
    )  # Ej: Ciclo I - 2026, Ciclo II - 2026
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Grupo(models.Model):
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    periodo = models.ForeignKey(PeriodoLectivo, on_delete=models.CASCADE)
    numero_grupo = models.PositiveIntegerField(default=1)
    profesor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'perfilusuario__rol': 'PROFESOR'},
    )
    cupo_maximo = models.PositiveIntegerField(default=30)

    class Meta:
        unique_together = ('curso', 'periodo', 'numero_grupo')

    def __str__(self):
        return (
            f'{self.curso.codigo} - Grupo {self.numero_grupo} ({self.periodo})'
        )
from django.db import models

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
    
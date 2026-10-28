from django.db import models
from academico.models import Grupo
from matricula.models import Matricula

# Definición del modelo Evaluacion para registrar los exámenes, tareas o pruebas asignadas a un grupo
class Evaluacion(models.Model):
    
    # Relación de muchos a uno (ForeignKey) con el modelo Grupo.
    # on_delete=models.CASCADE elimina las evaluaciones si se borra el grupo.
    # related_name='evaluaciones' permite consultar todas las evaluaciones de un grupo desde la instancia del grupo (ej: grupo.evaluaciones.all()).
    grupo = models.ForeignKey(
        Grupo, on_delete=models.CASCADE, related_name='evaluaciones'
    )
    
    # Campo de texto para almacenar el nombre o título de la evaluación (Ej: Examen 1, Tarea 2).
    nombre = models.CharField(max_length=50)
    
    # Campo numérico decimal (DecimalField) para definir el peso porcentual de la evaluación (Ej: 30.00).
    # max_digits=5 permite números de hasta 5 dígitos en total, y decimal_places=2 reserva 2 decimales.
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(porcentaje__gt=0)
                & models.Q(porcentaje__lte=100),
                name='evaluation_percentage_between_0_and_100',
            ),
        ]

    # Método especial para definir cómo se representará el objeto en texto (por ejemplo, en el panel de administración)
    def __str__(self):
        # Devuelve el nombre de la evaluación seguido del grupo entre paréntesis
        return f'{self.nombre} ({self.grupo})'


# Definición del modelo Calificacion para registrar la nota obtenida por un estudiante en una evaluación específica
class Calificacion(models.Model):
    
    # Relación de muchos a uno (ForeignKey) con el modelo Matricula.
    # Conecta la calificación directamente con la matrícula del estudiante en el grupo, 
    # permitiendo acceder al estudiante mediante 'matricula.estudiante'.
    # related_name='calificaciones' permite consultar todas las notas de un estudiante matriculado.
    matricula = models.ForeignKey(
        Matricula, on_delete=models.CASCADE, related_name='calificaciones'
    )
    
    # Relación de muchos a uno (ForeignKey) con el modelo Evaluacion.
    # Indica a qué examen o tarea corresponde esta nota. Si se borra la evaluación, se borra la calificación.
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE)
    
    # Campo numérico decimal para almacenar la calificación obtenida por el estudiante (Ej: 95.50).
    nota_obtenida = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('matricula', 'evaluacion'),
                name='uniq_grade_per_enrollment_evaluation',
            ),
            models.CheckConstraint(
                condition=models.Q(nota_obtenida__gte=0)
                & models.Q(nota_obtenida__lte=100),
                name='grade_between_0_and_100',
            ),
        ]

    # Método especial para definir la representación en texto del objeto Calificacion
    def __str__(self):
        # Devuelve el username del estudiante, el nombre de la evaluación y la nota obtenida
        return (
            f'{self.matricula.estudiante.username}: {self.evaluacion.nombre} ='
            f' {self.nota_obtenida}'
        )

from django.db import models
from django.contrib.auth.models import User
from academico.models import Grupo

# Definición del modelo Matricula para asociar a los estudiantes (usuarios) con los grupos de clases
class Matricula(models.Model):
    
    # Relación de muchos a uno (ForeignKey) con el modelo User de Django.
    # on_delete=models.CASCADE elimina la matrícula si se borra el usuario.
    # limit_choices_to restringe las opciones en los formularios de Django Admin 
    # para que solo se puedan seleccionar usuarios cuyo perfil tenga el rol 'ESTUDIANTE'.
    estudiante = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        limit_choices_to={'perfilusuario__rol': 'ESTUDIANTE'},
    )
    
    # Relación de muchos a uno (ForeignKey) con el modelo Grupo (proveniente de la app 'academico').
    # Si se elimina el grupo, también se eliminan sus matrículas asociadas.
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    
    # Fecha y hora en que se crea el registro de la matrícula. 
    # auto_now_add=True asigna automáticamente la fecha y hora actual al momento de la inserción.
    fecha_matricula = models.DateTimeField(auto_now_add=True)
    
    # Campo de texto con opciones para definir el estado actual de la matrícula.
    estado = models.CharField(
        max_length=20,
        choices=[
            ('MATRICULADO', 'Matriculado'),
            ('RETIRADO', 'Retirado'),
        ],
        default='MATRICULADO',
    )

    class Meta:
        # Restricción a nivel de base de datos para evitar que un mismo estudiante 
        # se matricule dos veces en el mismo grupo.
        unique_together = ('estudiante', 'grupo')

    # Método especial para definir la representación en texto del objeto (por ejemplo, en el admin de Django)
    def __str__(self):
        # Devuelve el nombre de usuario seguido de una flecha y la representación del grupo
        return f'{self.estudiante.username} -> {self.grupo}'
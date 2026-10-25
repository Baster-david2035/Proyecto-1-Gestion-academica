from django.contrib.auth.models import User
from django.db import models

# Definición del modelo PerfilUsuario para extender la información del usuario base de Django
class PerfilUsuario(models.Model):
    
    # Tupla de opciones para restringir y definir los roles permitidos en el sistema.
    # El primer valor se guarda en la base de datos, el segundo es el texto legible.
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('ESTUDIANTE', 'Estudiante'),
    )
    
    # Relación de uno a uno con el modelo de Usuario por defecto.
    # on_delete=models.CASCADE significa que si se elimina el User, también se eliminará este perfil automáticamente.
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # Campo de texto para almacenar el rol del usuario. 
    # Utiliza las opciones definidas arriba y tiene 'ESTUDIANTE' como valor por defecto.
    rol = models.CharField(max_length=20, choices=ROLES, default='ESTUDIANTE')
    
    # Campo opcional para almacenar el número de teléfono (puede quedar en blanco o nulo en la base de datos).
    telefono = models.CharField(max_length=15, blank=True, null=True)

    # Método especial para definir cómo se representará el objeto en formato de cadena (por ejemplo, en el panel de administración).
    def __str__(self):
        # Devuelve el nombre completo del usuario junto con su rol entre paréntesis.
        return f'{self.user.get_full_name()} ({self.rol})'
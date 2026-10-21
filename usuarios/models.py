from django.contrib.auth.models import User
from django.db import models

class PerfilUsuario(models.Model):
    ROLES = (
        ('ADMIN', 'Administrador'),
        ('PROFESOR', 'Profesor'),
        ('ESTUDIANTE', 'Estudiante'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES, default='ESTUDIANTE')
    telefono = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f'{self.user.get_full_name()} ({self.rol})'
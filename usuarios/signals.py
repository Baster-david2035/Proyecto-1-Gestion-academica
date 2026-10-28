from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PerfilUsuario


@receiver(post_save, sender=get_user_model())
def crear_perfil_administrador(sender, instance, created, **kwargs):
    """Give newly created Django staff accounts their matching API role."""
    if (created or instance.is_staff or instance.is_superuser) and (
        instance.is_staff or instance.is_superuser
    ):
        PerfilUsuario.objects.get_or_create(
            user=instance,
            defaults={'rol': 'ADMIN'},
        )

from django.conf import settings
from django.db import migrations


def create_admin_profiles(apps, schema_editor):
    User = apps.get_model(*settings.AUTH_USER_MODEL.split('.'))
    PerfilUsuario = apps.get_model('usuarios', 'PerfilUsuario')
    for user in User.objects.filter(is_staff=True) | User.objects.filter(is_superuser=True):
        PerfilUsuario.objects.get_or_create(
            user_id=user.pk,
            defaults={'rol': 'ADMIN'},
        )


class Migration(migrations.Migration):
    dependencies = [
        ('usuarios', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_admin_profiles, migrations.RunPython.noop),
    ]

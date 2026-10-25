from django.urls import path
from . import views

urlpatterns = [
    # Consultar el perfil del usuario autenticado
    path('perfil/',views.mi_perfil,name='mi_perfil'),

    # Listar todos los perfiles (solo administrador)
    path('perfiles/',views.listar_perfiles,name='listar_perfiles'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Listar o crear horarios
    path('horarios/',views.listar_crear_horarios,name='listar_crear_horarios'),

    # Consultar, modificar o eliminar un horario
    path('horarios/<int:pk>/', views.detalle_horario,name='detalle_horario'),
]
from django.urls import path
from . import views

urlpatterns = [
    # Evaluaciones
    path('evaluaciones/',views.listar_crear_evaluaciones,name='listar_crear_evaluaciones'),
    path('evaluaciones/<int:pk>/',views.detalle_evaluacion,name='detalle_evaluacion'),

    # Calificaciones
    path('calificaciones/',views.listar_crear_calificaciones,name='listar_crear_calificaciones'),
    path('calificaciones/<int:pk>/',views.detalle_calificacion,name='detalle_calificacion'),
]
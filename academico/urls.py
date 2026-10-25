from django.urls import path
from . import views

urlpatterns = [
    # Carreras
    path('carreras/',views.listar_crear_carreras,name='listar_crear_carreras'),
    path('carreras/<int:pk>/',views.detalle_carrera,name='detalle_carrera',),

    # Cursos
    path('cursos/',views.listar_crear_cursos,name='listar_crear_cursos'),
    path('cursos/<int:pk>/',views.detalle_curso,name='detalle_curso'),

    # Períodos lectivos
    path('periodos/',views.listar_crear_periodos,name='listar_crear_periodos'),
    path('periodos/<int:pk>/',views.detalle_periodo,name='detalle_periodo'),

    # Grupos
    path('grupos/',views.listar_crear_grupos,name='listar_crear_grupos'),
    path('grupos/<int:pk>/',views.detalle_grupo,name='detalle_grupo'),
]
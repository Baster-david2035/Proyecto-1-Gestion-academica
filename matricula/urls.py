from django.urls import path
from . import views

urlpatterns = [
    # Listar matrículas o crear una nueva
    path('',views.listar_crear_matriculas,name='listar_crear_matriculas'),

    # Consultar, modificar o eliminar una matrícula
    path('<int:pk>/',views.detalle_matricula,name='detalle_matricula'),
]
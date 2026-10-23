from django.contrib import admin
from .models import Carrera, Curso, Grupo, PeriodoLectivo

admin.site.register(Carrera)
admin.site.register(Curso)
admin.site.register(PeriodoLectivo)
admin.site.register(Grupo)
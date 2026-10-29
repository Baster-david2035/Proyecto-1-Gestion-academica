from decimal import Decimal
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

# Ajusta los imports según la estructura de tus apps
from usuarios.models import PerfilUsuario 
from academico.models import Carrera, Curso, PeriodoLectivo, Grupo
from calificaciones.models import Evaluacion, Calificacion
from matricula.models import Matricula


class CalificacionesPermisosTestCase(APITestCase):

    def setUp(self):
        # 1. Crear datos base académicos necesarios para las relaciones
        self.carrera = Carrera.objects.create(nombre="Ingeniería en Sistemas")
        self.curso = Curso.objects.create(nombre="Matemáticas I", carrera=self.carrera)
        self.periodo = PeriodoLectivo.objects.create(nombre="2026-I")

        # 2. Crear usuarios de prueba con sus roles
        # --- Administrador ---
        self.admin_user = User.objects.create_superuser(username="admin", password="password")
        self.admin_token = Token.objects.create(user=self.admin_user)

        # --- Profesor ---
        self.prof_user = User.objects.create_user(username="profesor", password="password")
        PerfilUsuario.objects.create(user=self.prof_user, rol="PROFESOR")
        self.prof_token = Token.objects.create(user=self.prof_user)

        # --- Estudiante ---
        self.est_user = User.objects.create_user(username="estudiante", password="password")
        PerfilUsuario.objects.create(user=self.est_user, rol="ESTUDIANTE")
        self.est_token = Token.objects.create(user=self.est_user)

        # 3. Crear un grupo asignado al profesor de prueba
        self.grupo_profe = Grupo.objects.create(
            curso=self.curso,
            periodo=self.periodo,
            profesor=self.prof_user
        )

        # 4. Crear otro grupo asignado a OTRO profesor (para probar restricciones cruzadas)
        self.otro_prof = User.objects.create_user(username="otro_prof", password="password")
        PerfilUsuario.objects.create(user=self.otro_prof, rol="PROFESOR")
        self.grupo_otro = Grupo.objects.create(
            curso=self.curso,
            periodo=self.periodo,
            profesor=self.otro_prof
        )

        # 5. Matricular al estudiante en el grupo del profesor principal
        self.matricula = Matricula.objects.create(
            estudiante=self.est_user,
            grupo=self.grupo_profe,
            estado="MATRICULADO"
        )

        # 6. Crear una evaluación inicial en el grupo del profesor
        self.evaluacion = Evaluacion.objects.create(
            grupo=self.grupo_profe,
            nombre="Examen Parcial 1",
            porcentaje=Decimal("50.00")
        )

        # URLs de ejemplo (asegúrate de que coincidan con tus names o usa las rutas directas)
        # Puedes definir name='lista-evaluaciones' en tus urls.py
        self.url_evaluaciones = "/api/calificaciones/evaluaciones/" # Ajusta según tu urls.py

    def test_estudiante_puede_ver_evaluaciones_de_su_grupo(self):
        """Un estudiante autenticado debe poder listar las evaluaciones de su grupo."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.est_token.key)
        response = self.client.get(self.url_evaluaciones, {"grupo": self.grupo_profe.pk})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

    def test_profesor_ajeno_no_puede_crear_evaluacion_en_grupo_ajeno(self):
        """Un profesor no puede crear evaluaciones en un grupo que no le pertenece."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.prof_token.key)
        
        data = {
            "grupo": self.grupo_otro.pk,
            "nombre": "Examen Ilegal",
            "porcentaje": "30.00"
        }
        response = self.client.post(self.url_evaluaciones, data)
        
        # Debe retornar prohibido (403) porque no imparte ese grupo
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_profesor_puede_crear_evaluacion_en_su_grupo(self):
        """Un profesor sí puede crear evaluaciones en su propio grupo."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.prof_token.key)
        
        data = {
            "grupo": self.grupo_profe.pk,
            "nombre": "Examen Parcial 2",
            "porcentaje": "50.00"
        }
        response = self.client.post(self.url_evaluaciones, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_estudiante_no_puede_crear_evaluaciones(self):
        """Un estudiante jamás debe poder crear evaluaciones (debe recibir 403)."""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.est_token.key)
        
        data = {
            "grupo": self.grupo_profe.pk,
            "nombre": "Examen Estudiante",
            "porcentaje": "20.00"
        }
        response = self.client.post(self.url_evaluaciones, data)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
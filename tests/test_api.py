from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import User
from rest_framework.test import APITestCase

from academico.models import Carrera, Curso, Grupo, PeriodoLectivo
from calificaciones.models import Calificacion, Evaluacion
from horarios.models import HorarioGrupo
from matricula.models import Matricula
from usuarios.models import PerfilUsuario


class AcademicApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('admin', 'admin@example.test', 'Admin-pass-123')
        self.professor = User.objects.create_user('professor', password='Professor-pass-123')
        PerfilUsuario.objects.create(user=self.professor, rol='PROFESOR')
        self.student = User.objects.create_user('student', password='Student-pass-123')
        PerfilUsuario.objects.create(user=self.student, rol='ESTUDIANTE')
        self.student2 = User.objects.create_user('student2', password='Student2-pass-123')
        PerfilUsuario.objects.create(user=self.student2, rol='ESTUDIANTE')
        self.other_professor = User.objects.create_user('professor2', password='Professor2-pass-123')
        PerfilUsuario.objects.create(user=self.other_professor, rol='PROFESOR')

        self.career = Carrera.objects.create(codigo='INF-01', nombre='Informática')
        self.course = Curso.objects.create(
            codigo='INF-101', nombre='Fundamentos', creditos=4, carrera=self.career
        )
        self.period = PeriodoLectivo.objects.create(
            nombre='Ciclo 2026-I', fecha_inicio=date(2026, 1, 1),
            fecha_fin=date(2026, 6, 30), activo=True,
        )
        self.group = Grupo.objects.create(
            curso=self.course, periodo=self.period, profesor=self.professor,
            numero_grupo=1, cupo_maximo=30,
        )
        self.group2 = Grupo.objects.create(
            curso=self.course, periodo=self.period, profesor=self.other_professor,
            numero_grupo=2, cupo_maximo=30,
        )
        self.enrollment = Matricula.objects.create(estudiante=self.student, grupo=self.group)
        self.evaluation = Evaluacion.objects.create(
            grupo=self.group, nombre='Parcial', porcentaje=Decimal('50.00')
        )

    def as_user(self, user):
        self.client.force_authenticate(user=user)

    def test_unauthenticated_api_returns_401(self):
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get('/api/academico/carreras/').status_code, 401)

    def test_token_endpoint_returns_token_for_valid_credentials(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/token/', {'username': 'student', 'password': 'Student-pass-123'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('token', response.data)

    def test_authenticated_user_can_list_careers(self):
        self.as_user(self.student)
        self.assertEqual(self.client.get('/api/academico/carreras/').status_code, 200)

    def test_student_cannot_create_career(self):
        self.as_user(self.student)
        response = self.client.post('/api/academico/carreras/', {'codigo': 'ADM-01', 'nombre': 'Administración'})
        self.assertEqual(response.status_code, 403)

    def test_admin_can_create_career(self):
        self.as_user(self.admin)
        response = self.client.post('/api/academico/carreras/', {'codigo': 'ADM-01', 'nombre': 'Administración'})
        self.assertEqual(response.status_code, 201)

    def test_duplicate_career_code_is_rejected(self):
        self.as_user(self.admin)
        response = self.client.post('/api/academico/carreras/', {'codigo': 'inf-01', 'nombre': 'Otra'})
        self.assertEqual(response.status_code, 400)

    def test_career_search_and_pagination(self):
        self.as_user(self.student)
        response = self.client.get('/api/academico/carreras/?search=inform&page=1&page_size=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)

    def test_invalid_ordering_returns_400(self):
        self.as_user(self.student)
        self.assertEqual(self.client.get('/api/academico/carreras/?ordering=--id').status_code, 400)

    def test_group_filters_can_be_combined(self):
        self.as_user(self.student)
        response = self.client.get(f'/api/academico/grupos/?curso={self.course.pk}&periodo={self.period.pk}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 2)

    def test_invalid_numeric_filter_returns_400(self):
        self.as_user(self.student)
        self.assertEqual(self.client.get('/api/academico/grupos/?curso=abc').status_code, 400)

    def test_student_can_enroll_self(self):
        self.as_user(self.student2)
        response = self.client.post('/api/matricula/', {'grupo': self.group.pk})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['estudiante'], self.student2.pk)

    def test_duplicate_enrollment_is_rejected(self):
        self.as_user(self.student)
        self.assertEqual(self.client.post('/api/matricula/', {'grupo': self.group.pk}).status_code, 400)

    def test_enrollment_respects_group_capacity(self):
        self.group.cupo_maximo = 1
        self.group.save()
        self.as_user(self.admin)
        response = self.client.post('/api/matricula/', {'estudiante': self.student2.pk, 'grupo': self.group.pk})
        self.assertEqual(response.status_code, 400)

    def test_enrollment_rejects_inactive_period(self):
        self.period.activo = False
        self.period.save()
        self.as_user(self.student2)
        self.assertEqual(self.client.post('/api/matricula/', {'grupo': self.group.pk}).status_code, 400)

    def test_prerequisite_requires_a_weighted_final_grade_of_at_least_seventy(self):
        advanced = Curso.objects.create(
            codigo='INF-201', nombre='Avanzado', creditos=4, carrera=self.career,
        )
        advanced.prerrequisitos.add(self.course)
        advanced_group = Grupo.objects.create(
            curso=advanced, periodo=self.period, profesor=self.professor,
            numero_grupo=1, cupo_maximo=30,
        )
        self.as_user(self.student)
        rejected = self.client.post('/api/matricula/', {'grupo': advanced_group.pk})
        self.assertEqual(rejected.status_code, 400)

        second_evaluation = Evaluacion.objects.create(
            grupo=self.group, nombre='Final', porcentaje=Decimal('50.00'),
        )
        Calificacion.objects.create(
            matricula=self.enrollment, evaluacion=self.evaluation,
            nota_obtenida=Decimal('100.00'),
        )
        Calificacion.objects.create(
            matricula=self.enrollment, evaluacion=second_evaluation,
            nota_obtenida=Decimal('100.00'),
        )
        accepted = self.client.post('/api/matricula/', {'grupo': advanced_group.pk})
        self.assertEqual(accepted.status_code, 201)

    def test_student_enrollment_rejects_conflicting_class_schedules(self):
        HorarioGrupo.objects.create(
            grupo=self.group, dia='LUN', hora_inicio=time(8),
            hora_fin=time(10), aula='A-1',
        )
        HorarioGrupo.objects.create(
            grupo=self.group2, dia='LUN', hora_inicio=time(9),
            hora_fin=time(11), aula='A-2',
        )
        self.as_user(self.student)
        response = self.client.post('/api/matricula/', {'grupo': self.group2.pk})
        self.assertEqual(response.status_code, 400)

    def test_student_only_sees_own_enrollments(self):
        Matricula.objects.create(estudiante=self.student2, grupo=self.group2)
        self.as_user(self.student)
        response = self.client.get('/api/matricula/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['estudiante'], self.student.pk)

    def test_student_cannot_create_evaluation(self):
        self.as_user(self.student)
        response = self.client.post('/api/evaluaciones/', {
            'grupo': self.group.pk, 'nombre': 'Tarea', 'porcentaje': '20.00',
        })
        self.assertEqual(response.status_code, 403)

    def test_assigned_professor_can_create_evaluation(self):
        self.as_user(self.professor)
        response = self.client.post('/api/evaluaciones/', {
            'grupo': self.group.pk, 'nombre': 'Tarea', 'porcentaje': '25.00',
        })
        self.assertEqual(response.status_code, 201)

    def test_evaluation_total_cannot_exceed_one_hundred(self):
        self.as_user(self.professor)
        response = self.client.post('/api/evaluaciones/', {
            'grupo': self.group.pk, 'nombre': 'Final', 'porcentaje': '60.01',
        })
        self.assertEqual(response.status_code, 400)

    def test_teacher_cannot_manage_another_teachers_evaluation(self):
        evaluation = Evaluacion.objects.create(grupo=self.group2, nombre='Prueba', porcentaje=20)
        self.as_user(self.professor)
        self.assertEqual(self.client.delete(f'/api/evaluaciones/{evaluation.pk}/').status_code, 404)

    def test_percentages_endpoint_reports_remaining_percentage(self):
        self.as_user(self.professor)
        response = self.client.get(f'/api/califica/{self.group.pk}/validar-porcentajes/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['porcentaje_faltante'], '50.00')

    def test_student_cannot_register_grade(self):
        self.as_user(self.student)
        response = self.client.post('/api/calificaciones/', {
            'matricula': self.enrollment.pk, 'evaluacion': self.evaluation.pk,
            'nota_obtenida': '90.00',
        })
        self.assertEqual(response.status_code, 403)

    def test_assigned_professor_can_register_grade(self):
        self.as_user(self.professor)
        response = self.client.post('/api/calificaciones/', {
            'matricula': self.enrollment.pk, 'evaluacion': self.evaluation.pk,
            'nota_obtenida': '90.00',
        })
        self.assertEqual(response.status_code, 201)

    def test_grade_outside_zero_to_one_hundred_is_rejected(self):
        self.as_user(self.professor)
        response = self.client.post('/api/calificaciones/', {
            'matricula': self.enrollment.pk, 'evaluacion': self.evaluation.pk,
            'nota_obtenida': '101.00',
        })
        self.assertEqual(response.status_code, 400)

    def test_grade_from_different_group_is_rejected(self):
        other_evaluation = Evaluacion.objects.create(grupo=self.group2, nombre='Otro grupo', porcentaje=20)
        self.as_user(self.professor)
        response = self.client.post('/api/calificaciones/', {
            'matricula': self.enrollment.pk, 'evaluacion': other_evaluation.pk,
            'nota_obtenida': '90.00',
        })
        self.assertEqual(response.status_code, 400)

    def test_student_only_sees_own_grades(self):
        grade = Calificacion.objects.create(matricula=self.enrollment, evaluacion=self.evaluation, nota_obtenida=90)
        other_enrollment = Matricula.objects.create(estudiante=self.student2, grupo=self.group2)
        other_evaluation = Evaluacion.objects.create(grupo=self.group2, nombre='Otro', porcentaje=20)
        Calificacion.objects.create(matricula=other_enrollment, evaluacion=other_evaluation, nota_obtenida=80)
        self.as_user(self.student)
        response = self.client.get('/api/calificaciones/')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], grade.pk)

    def test_student_cannot_edit_own_grade(self):
        grade = Calificacion.objects.create(matricula=self.enrollment, evaluacion=self.evaluation, nota_obtenida=90)
        self.as_user(self.student)
        response = self.client.patch(f'/api/calificaciones/{grade.pk}/', {'nota_obtenida': '95.00'})
        self.assertEqual(response.status_code, 403)

    def test_schedule_rejects_overlapping_room(self):
        HorarioGrupo.objects.create(grupo=self.group, dia='LUN', hora_inicio=time(8), hora_fin=time(10), aula='A-1')
        self.as_user(self.admin)
        response = self.client.post('/api/horarios/', {
            'grupo': self.group2.pk, 'dia': 'LUN', 'hora_inicio': '09:00',
            'hora_fin': '11:00', 'aula': 'a-1',
        })
        self.assertEqual(response.status_code, 400)

    def test_schedule_rejects_end_before_start(self):
        self.as_user(self.admin)
        response = self.client.post('/api/horarios/', {
            'grupo': self.group.pk, 'dia': 'LUN', 'hora_inicio': '10:00',
            'hora_fin': '09:00', 'aula': 'A-1',
        })
        self.assertEqual(response.status_code, 400)

    def test_student_cannot_create_schedule(self):
        self.as_user(self.student)
        response = self.client.post('/api/horarios/', {
            'grupo': self.group.pk, 'dia': 'LUN', 'hora_inicio': '08:00',
            'hora_fin': '09:00', 'aula': 'A-1',
        })
        self.assertEqual(response.status_code, 403)

    def test_schedule_list_is_paginated_and_filterable(self):
        HorarioGrupo.objects.create(grupo=self.group, dia='LUN', hora_inicio=time(8), hora_fin=time(9), aula='A-1')
        self.as_user(self.admin)
        response = self.client.get('/api/horarios/?dia=LUN&page=1&page_size=1')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(len(response.data['results']), 1)


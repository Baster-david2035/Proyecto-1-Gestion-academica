from rest_framework import serializers
from .models import Matricula


# Serializer para transformar el modelo Matricula en JSON (y viceversa).
class MatriculaSerializer(serializers.ModelSerializer):

    estudiante_username = serializers.ReadOnlyField(
        source='estudiante.username'
    )

    grupo_detalle = serializers.ReadOnlyField(
        source='grupo.__str__'
    )

    class Meta:
        model = Matricula
        fields = [
            'id',
            'estudiante',
            'estudiante_username',
            'grupo',
            'grupo_detalle',
            'fecha_matricula',
            'estado',
        ]
        read_only_fields = ['fecha_matricula']

    def validate_estudiante(self, estudiante):
        # Comprobar que el usuario tenga un perfil de estudiante.
        perfil = getattr(estudiante, 'perfilusuario', None)

        if perfil is None or perfil.rol != 'ESTUDIANTE':
            raise serializers.ValidationError(
                'El usuario seleccionado debe tener el rol ESTUDIANTE.'
            )

        return estudiante

    def validate(self, attrs):
        # Obtener los datos nuevos o conservar los existentes al actualizar.
        estudiante = attrs.get(
            'estudiante',
            getattr(self.instance, 'estudiante', None)
        )
        grupo = attrs.get(
            'grupo',
            getattr(self.instance, 'grupo', None)
        )

        # Impedir matrículas duplicadas del mismo estudiante en el grupo.
        if estudiante is not None and grupo is not None:
            estado_destino = attrs.get(
                'estado',
                getattr(self.instance, 'estado', 'MATRICULADO'),
            )
            es_alta_activa = (
                estado_destino == 'MATRICULADO'
                and (
                    self.instance is None
                    or self.instance.estado != 'MATRICULADO'
                    or self.instance.grupo_id != grupo.pk
                )
            )
            if es_alta_activa and not grupo.periodo.activo:
                raise serializers.ValidationError({
                    'grupo': 'No se puede matricular en un período inactivo.'
                })

            matriculas = Matricula.objects.filter(
                estudiante=estudiante,
                grupo=grupo
            )

            # Al actualizar, excluir la matrícula actual.
            if self.instance is not None:
                matriculas = matriculas.exclude(pk=self.instance.pk)

            if matriculas.exists():
                raise serializers.ValidationError({
                    'grupo': (
                        'Este estudiante ya tiene una matrícula '
                        'registrada para ese grupo.'
                    )
                })

            # El cupo se verifica también al editar una matrícula para que
            # una operación administrativa no rebase la capacidad del grupo.
            activas = Matricula.objects.filter(
                grupo=grupo,
                estado='MATRICULADO',
            )
            if self.instance is not None:
                activas = activas.exclude(pk=self.instance.pk)
            if (
                estado_destino == 'MATRICULADO'
                and activas.count() >= grupo.cupo_maximo
            ):
                raise serializers.ValidationError({
                    'grupo': 'El grupo ya alcanzó su cupo máximo.'
                })

            # Convención del proyecto: una nota final de 70/100 aprueba un
            # curso y habilita sus cursos dependientes.
            from django.db.models import DecimalField, ExpressionWrapper, F, Sum
            from calificaciones.models import Calificacion

            requisitos = grupo.curso.prerrequisitos.all()
            notas_finales = Calificacion.objects.filter(
                matricula__estudiante=estudiante,
                evaluacion__grupo__curso__in=requisitos,
            ).values(
                'evaluacion__grupo_id',
                'evaluacion__grupo__curso_id',
            ).annotate(
                porcentaje_total=Sum('evaluacion__porcentaje'),
                nota_final=Sum(ExpressionWrapper(
                    F('nota_obtenida') * F('evaluacion__porcentaje') / 100,
                    output_field=DecimalField(max_digits=10, decimal_places=4),
                )),
            ).filter(porcentaje_total=100, nota_final__gte=70)
            aprobados = {
                fila['evaluacion__grupo__curso_id']
                for fila in notas_finales
            }
            faltantes = [
                requisito for requisito in requisitos
                if requisito.pk not in aprobados
            ]
            if faltantes:
                raise serializers.ValidationError({
                    'grupo': 'El estudiante no ha aprobado todos los prerrequisitos del curso.'
                })

            # Evita choques de horario con otros grupos en los que ya está
            # matriculado el estudiante.
            from horarios.models import HorarioGrupo

            horarios_actuales = HorarioGrupo.objects.filter(
                grupo__matricula__estudiante=estudiante,
                grupo__matricula__estado='MATRICULADO',
            ).exclude(grupo=grupo)
            horarios_nuevos = HorarioGrupo.objects.filter(grupo=grupo)
            for horario in horarios_nuevos:
                if horarios_actuales.filter(
                    dia=horario.dia,
                    hora_inicio__lt=horario.hora_fin,
                    hora_fin__gt=horario.hora_inicio,
                ).exists():
                    raise serializers.ValidationError({
                        'grupo': 'El horario del grupo choca con otra matrícula del estudiante.'
                    })

        return attrs

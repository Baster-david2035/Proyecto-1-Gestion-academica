from rest_framework import serializers
from .models import Evaluacion, Calificacion
from decimal import Decimal


# Serializer para transformar el modelo Evaluacion en formato JSON (y viceversa)
class EvaluacionSerializer(serializers.ModelSerializer):

    grupo_detalle = serializers.ReadOnlyField(source='grupo.__str__')

    class Meta:
        model = Evaluacion
        fields = ['id', 'grupo', 'grupo_detalle', 'nombre', 'porcentaje']

    def validate_porcentaje(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError(
                "El porcentaje debe ser mayor que 0."
            )

        if value > Decimal('100'):
            raise serializers.ValidationError(
                "El porcentaje no puede superar el 100%."
            )

        return value

    def validate(self, data):
        grupo = data.get(
            'grupo',
            self.instance.grupo if self.instance else None
        )

        porcentaje = data.get(
            'porcentaje',
            self.instance.porcentaje if self.instance else None
        )

        if grupo is None or porcentaje is None:
            return data

        # Obtener las evaluaciones que ya pertenecen al grupo.
        evaluaciones = Evaluacion.objects.filter(grupo=grupo)

        # Al actualizar, excluir la evaluación actual para no sumarla dos veces.
        if self.instance:
            evaluaciones = evaluaciones.exclude(pk=self.instance.pk)

        # Sumar los porcentajes existentes.
        total_actual = sum(
            (
                evaluacion.porcentaje
                for evaluacion in evaluaciones
            ),
            Decimal('0')
        )

        # Sumar el porcentaje nuevo o actualizado.
        total_nuevo = total_actual + porcentaje

        if total_nuevo > Decimal('100'):
            raise serializers.ValidationError({
                'porcentaje': (
                    f'El grupo ya tiene evaluaciones que suman '
                    f'{total_actual}%. Con este cambio, el total sería '
                    f'{total_nuevo}%, y no puede superar el 100%.'
                )
            })

        return data


# Serializer para transformar el modelo Calificacion en formato JSON (y viceversa)
class CalificacionSerializer(serializers.ModelSerializer):

    estudiante_nombre = serializers.ReadOnlyField(
        source='matricula.estudiante.get_full_name'
    )

    evaluacion_nombre = serializers.ReadOnlyField(
        source='evaluacion.nombre'
    )

    class Meta:
        model = Calificacion
        fields = [
            'id',
            'matricula',
            'estudiante_nombre',
            'evaluacion',
            'evaluacion_nombre',
            'nota_obtenida',
        ]

    def validate_nota_obtenida(self, nota):
        if nota < 0 or nota > 100:
            raise serializers.ValidationError(
                'La nota debe estar entre 0 y 100.'
            )

        return nota

    def validate(self, attrs):
        matricula = attrs.get(
            'matricula',
            getattr(self.instance, 'matricula', None)
        )

        evaluacion = attrs.get(
            'evaluacion',
            getattr(self.instance, 'evaluacion', None)
        )

        if matricula is not None and evaluacion is not None:

            # La matrícula y la evaluación deben pertenecer al mismo grupo.
            if matricula.grupo_id != evaluacion.grupo_id:
                raise serializers.ValidationError({
                    'evaluacion': (
                        'La evaluación debe pertenecer al grupo '
                        'en el que está matriculado el estudiante.'
                    )
                })

            # No permitir calificar a un estudiante retirado.
            if matricula.estado != 'MATRICULADO':
                raise serializers.ValidationError({
                    'matricula': (
                        'No se pueden registrar calificaciones '
                        'para una matrícula retirada.'
                    )
                })

            # Evitar calificaciones duplicadas.
            calificaciones = Calificacion.objects.filter(
                matricula=matricula,
                evaluacion=evaluacion
            )

            # Excluir el registro actual cuando se está actualizando.
            if self.instance is not None:
                calificaciones = calificaciones.exclude(
                    pk=self.instance.pk
                )

            if calificaciones.exists():
                raise serializers.ValidationError({
                    'evaluacion': (
                        'Esta matrícula ya tiene una calificación '
                        'registrada para esa evaluación.'
                    )
                })

        return attrs
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

    return attrs
from django.contrib.auth.models import User
from rest_framework import serializers
from .models import PerfilUsuario


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    # Permite asociar un usuario existente al crear el perfil mediante su ID
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), source='user', write_only=True
    )

    class Meta:
        model = PerfilUsuario
        fields = ['id', 'user', 'user_id', 'rol', 'telefono']
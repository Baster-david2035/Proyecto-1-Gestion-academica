from django.contrib.auth.models import User
from rest_framework import serializers
from .models import PerfilUsuario


# Serializer para transformar el modelo nativo de Usuario de Django en JSON (y viceversa)
class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        # Campos que se expondrán en la API cuando se consulte o serialice un usuario
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


# Serializer para el modelo PerfilUsuario que incluye la información del usuario asociado
class PerfilUsuarioSerializer(serializers.ModelSerializer):
    # Campo anidado para mostrar los detalles completos del usuario al leer (GET).
    # Se define como read_only=True porque este objeto se gestiona a través de 'user_id' al escribir.
    user = UserSerializer(read_only=True)
    
    # Campo de escritura (POST/PUT/PATCH) que permite asociar un usuario existente 
    # enviando únicamente su ID. 'source="user"' indica que este valor se guardará en el campo 'user' del modelo.
    user_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='user', write_only=True)
    class Meta:
        model = PerfilUsuario
        # Lista de campos expuestos por la API para el perfil
        fields = ['id', 'user', 'user_id', 'rol', 'telefono']
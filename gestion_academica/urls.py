"""
URL configuration for gestion_academica project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('admin/', admin.site.urls),
    # Ruta para obtener el token de autenticación (Login)
    path('api/token/', obtain_auth_token, name='api_token_auth'),
    # Inclusión de las rutas de cada módulo
    path('api/usuarios/', include('usuarios.urls')),
    path('api/academico/', include('academico.urls')),
    path('api/matricula/', include('matricula.urls')),
    path('api/calificaciones/', include('calificaciones.urls')),
    path('api/horarios/', include('horarios.urls')),
]
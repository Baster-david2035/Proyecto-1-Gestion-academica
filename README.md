Aqui haremos la explicacion oficial del proyecto
# Sistema de Gestión Académica - API REST (Django)

Proyecto backend desarrollado con Django para la gestión académica de una institución educativa

Modulos del sistema
El backend esta compuesto por 5 modulos principales:
- Usuarios: Control de perfiles (Administradores, Profesores, Estudiantes) y autenticación por tokens.
- Académico: Gestión de carreras, planes de estudio, cursos, periodos lectivos y grupos.
- Matrícula: Inscripción de estudiantes en grupos con validaciones relacionales.
- Calificaciones: Registro de evaluaciones y control de notas parciales/finales.
- Horarios: Asignación de días, horas y aulas por grupo.

Pruebas y documentacion
- Colección de Postman: Se incluye el archivo JSON con los endpoints listos para importar y probar en la carpeta raíz o de documentación.
- Pruebas Automatizadas: Ejecuta los tests del sistema.

Podemos probarlo con el comando en terminal de python manage.py test

## Instalación y Configuración

1. Clonar el repositorio:
   bash
   git clone 

2. Crear y activar entorno virtual
    bash o terminal
    python -m venv venv
    venv\Scripts\activate

3. Instalar las dependencias
    terminal
    pip install -r requirements.txt

4. Configurar las variables del .env
    creamos el archivo .env
    Configura los datos de acceso a tu base de datos

5. Aplicar las migraciones
    python manage.py makemigrations
    python manage.py migrate

6. Crea un superusuario para ser admin
    python manage.py createsuperuser
    username: root
    password: root
    email: root@gmail.com

7. Ejecutar el servidor de desarrollo
    python manage.py runserver
    La API estará disponible en http://127.0.0.1:8000/
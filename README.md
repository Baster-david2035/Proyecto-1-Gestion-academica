Aqui haremos la explicacion oficial del proyecto
Sistema de Gestión Académica - API REST (Django)

Proyecto backend desarrollado con Django para la gestión académica de una institución educativa

Modulos del sistema
El backend esta compuesto por 5 modulos principales:
- Usuarios: Control de perfiles (Administradores, Profesores, Estudiantes) y autenticación por tokens.
- Académico: Gestión de carreras, planes de estudio, cursos, periodos lectivos y grupos.
- Matrícula: Inscripción de estudiantes en grupos con validaciones relacionales.
- Calificaciones: Registro de evaluaciones y control de notas parciales/finales.
- Horarios: Asignación de días, horas y aulas por grupo.

Modelo entidad-relacion
Carrera (1) ------< (Curso): Una carrera tiene muchos cursos; un curso pertenece a una sola carrera.
Curso (1) ------< (Grupo): Un curso se abre en múltiples grupos a lo largo de los períodos.
PeriodoLectivo (1) ------< (Grupo): Un período lectivo contiene muchos grupos de clases.
User (Profesor) (1) ------< (Grupo): Un profesor puede impartir varios grupos.
User (Estudiante) (N) <---> (Grupo) (M): Relación de muchos a muchos gestionada a través de la entidad Matricula. Un estudiante matricula muchos grupos, y un grupo tiene muchos estudiantes matriculados.
Grupo (1) ------< (Evaluacion): Un grupo define varias evaluaciones (exámenes, tareas, etc.).
Matricula (1) ------< (Calificacion): Una matrícula de estudiante acumula notas para las diferentes evaluaciones.
Evaluacion (1) ------< (Calificacion): Una evaluación tiene las calificaciones de los distintos estudiantes matriculados.
Grupo (1) ------< (HorarioGrupo): Un grupo tiene asignados uno o varios bloques de horarios y aulas.


Pruebas y documentacion
- Colección de Postman: Se incluye el archivo JSON con los endpoints listos para importar y probar en la carpeta raíz o de documentación.
- Pruebas Automatizadas: Ejecuta los tests del sistema.

Podemos probarlo con el comando en terminal de python manage.py test

Instalación y Configuración

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
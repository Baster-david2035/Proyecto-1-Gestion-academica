# Sistema de Gestión Académica

API REST construida con Django y Django REST Framework para gestionar usuarios, carreras, cursos, períodos lectivos, grupos, matrículas, evaluaciones, calificaciones y horarios. El backend utiliza MySQL 8.4 y autenticación por token. No incluye interfaz web para estudiantes.

## Requisitos

- Python 3.11 o 3.12.
- MySQL 8.0.16 o posterior (recomendado MySQL 8.4).
- Docker Compose, o un servidor MySQL local.

## Inicio rápido en Windows

Desde PowerShell, en la carpeta del proyecto:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Edita `.env` y cambia `DJANGO_SECRET_KEY` y las contraseñas de desarrollo. Levanta MySQL con Docker Compose:

```powershell
docker compose up -d db
```

Espera a que MySQL esté saludable y prepara la aplicación:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

La API queda en `http://127.0.0.1:8000/` y el panel de administración en `http://127.0.0.1:8000/admin/`.

El servicio Compose guarda sus datos en el volumen `mysql_data`; parar el servicio con `docker compose down` no elimina esos datos. Para empezar con una base vacía, elimina el volumen conscientemente con `docker compose down -v`.

### MySQL instalado localmente

Crea una base de datos `gestion_academica` con `utf8mb4`, un usuario de aplicación y la base de pruebas `test_gestion_academica`. Configura los valores en `.env`. Para que `python manage.py test` cree y elimine su base aislada, el usuario requiere permisos `CREATE` y `DROP` sobre esa instancia. No uses credenciales de producción para correr pruebas.

## Usuarios y permisos

El comando `createsuperuser` crea el perfil API de administrador automáticamente. En `/admin/`, crea los usuarios regulares y sus perfiles con los roles `ESTUDIANTE` y `PROFESOR` antes de crear grupos o probar las solicitudes Postman. El campo profesor de cada grupo debe apuntar a un usuario con perfil profesor.

| Rol | Lectura | Escritura |
| --- | --- | --- |
| Administrador | Todos los recursos | Todos los recursos |
| Profesor | Catálogo académico general; matrículas, grupos, evaluaciones, notas y horarios propios | Evaluaciones, notas y horarios de grupos que imparte |
| Estudiante | Catálogo y grupos disponibles; sus matrículas y notas; evaluaciones y horarios de sus grupos activos | Solicitar matrícula propia |

Los cambios académicos generales (carreras, cursos, períodos y grupos) y las operaciones de modificación/eliminación de matrículas son exclusivas del administrador. Las solicitudes sin token responden `401`; las solicitudes autenticadas sin permiso responden `403` (o `404` cuando el objeto no pertenece al conjunto visible para el rol).

## Autenticación

Solicita un token con:

```http
POST /api/token/
Content-Type: application/json

{"username":"usuario","password":"contraseña"}
```

Envía el token en las demás solicitudes:

```http
Authorization: Token <token>
```

## Endpoints principales

| Módulo | Rutas |
| --- | --- |
| Usuarios | `GET /api/usuarios/perfil/`, `GET /api/usuarios/perfiles/` (administrador) |
| Académico | CRUD `/api/academico/carreras/`, `/cursos/`, `/periodos/` y `/grupos/` |
| Matrícula | CRUD `/api/matricula/` |
| Calificaciones | CRUD `/api/evaluaciones/`, `/api/calificaciones/`; `GET /api/califica/{grupo_id}/validar-porcentajes/` |
| Horarios | CRUD `/api/horarios/` |

Los listados académicos admiten `page` y `page_size` (máximo 50), búsqueda con `search`, ordenamiento con `ordering`, y filtros por relaciones como `curso`, `periodo`, `carrera`, `grupo`, `matricula` y `evaluacion`. Matrículas y horarios también se paginan. Los filtros numéricos inválidos devuelven `400`.

## Reglas de negocio implementadas

- Códigos de carrera y curso únicos; nombres y códigos no vacíos.
- Los cursos no se pueden prerequerir a sí mismos, crear ciclos ni usar prerrequisitos de otra carrera.
- Fin de período posterior o igual al inicio; grupo con número y cupo mayores que cero; profesor asignado con rol profesor.
- Una matrícula solo se crea en un período activo, respeta el cupo, no se duplica, valida prerrequisitos con nota final ponderada de al menos 70/100 (con porcentajes que suman 100%) y evita choques de horario del estudiante.
- Una evaluación tiene porcentaje mayor que cero y menor o igual a 100; la suma por grupo no supera 100%.
- La nota está entre 0 y 100; matrícula y evaluación pertenecen al mismo grupo; una nota por evaluación y matrícula; no se califica una matrícula retirada.
- Los horarios tienen duración positiva y no se solapan para el grupo ni para el aula.

## Migraciones y pruebas

Las migraciones versionadas están en cada aplicación. Al cambiar modelos:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Ejecuta las pruebas con:

```powershell
python manage.py test
```

Django crea una base temporal MySQL configurada como `MYSQL_TEST_DATABASE` y la elimina al terminar. Ejecuta las pruebas contra una base de desarrollo; el usuario MySQL debe poder crear y eliminar la base de pruebas.

## Postman

Importa `postman/gestion_academica.postman_collection.json` y `postman/gestion_academica.postman_environment.json`. Configura `adminUsername`, `adminPassword`, `studentId` y `professorId`. Ejecuta la colección en orden: primero obtiene un token, crea una carrera, curso, período y grupo; luego matricula, crea evaluación y nota y programa un horario. Usa una base vacía o códigos nuevos para que los valores únicos no choquen. La colección incluye más de 20 solicitudes con pruebas de respuesta en los pasos de creación y autenticación.

## Configuración y despliegue

`.env` no se versiona. No publiques claves, contraseñas ni tokens. En producción define una clave secreta aleatoria, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS` con los dominios reales, un MySQL administrado y transporte HTTPS. `compose.yaml` es solo un servicio de base de datos local; el servidor Django se inicia por separado.

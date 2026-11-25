# Frontend – Sistema de Gestión Académica (Proyecto 2)

Aplicación web de una sola página (SPA) hecha con **React + Vite + JavaScript**, **Bootstrap 5** y **React Router 6**. Consume la API REST del Proyecto 1, que está en la raíz de este mismo repositorio. No usa datos simulados: todo se lee y se guarda en la base de datos por medio de la API.

## Requisitos

- Node.js 20 o superior (probado con Node 26 LTS) y npm.
- El backend del Proyecto 1 funcionando (ver el `README.md` de la raíz).

## Cómo ejecutar el proyecto

### 1. Levantar el backend (Django)

Desde la raíz del repositorio, siguiendo el README principal:

```powershell
.\.venv\Scripts\Activate.ps1
docker compose up -d db
python manage.py migrate
python manage.py runserver
```

La API queda en `http://127.0.0.1:8000/api/`.

### 2. Levantar el frontend (React)

En otra terminal:

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Abrir `http://localhost:5173`.

## Variables de entorno

Archivo `.env` (copiado de `.env.example`, sin secretos):

| Variable | Valor por defecto | Para qué sirve |
| --- | --- | --- |
| `VITE_API_URL` | `/api` | Ruta base que usa React para llamar a la API. Está centralizada en `src/services/api.js`. |
| `VITE_PROXY_TARGET` | `http://127.0.0.1:8000` | Dirección del servidor Django a la que Vite reenvía las peticiones. |

## Configuración de CORS

React corre en el puerto 5173 y Django en el 8000, así que el navegador los trata como orígenes distintos (CORS).

Para no modificar el backend del Proyecto 1, usamos el **proxy de Vite** (ver `vite.config.js`). El navegador le pide `/api/...` al mismo servidor de Vite y Vite se lo pasa a Django. Para el navegador todo viene del mismo origen, así que no aparece el error de CORS y **no hace falta instalar `django-cors-headers`**.

> Si en algún momento se quiere servir el frontend separado de Vite (por ejemplo, con `npm run build` en otro servidor), habría que agregar `django-cors-headers` al backend con `CORS_ALLOWED_ORIGINS` apuntando al dominio del frontend.

## Usuarios de prueba (ficticios)

Se crean desde `http://127.0.0.1:8000/admin/` con un superusuario. Cada usuario necesita un **Perfil de usuario** con su rol. Sugerencia para la demostración:

| Usuario | Rol | Uso en la demo |
| --- | --- | --- |
| `admin_demo` | ADMIN (superusuario) | Ve y gestiona todo |
| `profe_demo` | PROFESOR | Gestiona horarios, evaluaciones y notas de sus grupos |
| `estu_demo` | ESTUDIANTE | Solo consulta; solicita su propia matrícula |

Las contraseñas las define cada equipo en su base local y **no se suben al repositorio**.

## Autenticación y sesión

- El login hace `POST /api/token/` y guarda el token en `localStorage`.
- Cada petición envía `Authorization: Token <token>` (DRF usa el prefijo `Token`, no `Bearer`).
- La sesión se comparte entre páginas con un Context (`src/context/AuthContext.jsx`). Al iniciar sesión se consulta `GET /api/usuarios/perfil/` para saber el nombre y el rol.
- Las rutas privadas están dentro de `RutaProtegida`. Si no hay token, redirige a `/login`.
- Si Django responde **401** (token inválido), se borra el token y se vuelve al login con un aviso.
- Si responde **403**, se muestra el mensaje del servidor. Los botones se ocultan según el rol solo por comodidad: **la seguridad real la aplica Django**.

### Limitación: el token no se revoca en el servidor

El backend no tiene un endpoint de logout. Al cerrar sesión, el frontend **solo borra el token del navegador**. El token sigue siendo válido en Django hasta que un administrador lo elimine desde `/admin/` (sección *Tokens*).

## Estructura de carpetas

```
src/
├─ services/api.js        URL base, token, fetch con manejo de errores
├─ context/AuthContext.jsx  Sesión compartida (login, logout, rol)
├─ components/            Piezas reutilizables
│  ├─ Layout, BarraSuperior, MenuLateral, RutaProtegida
│  └─ Alerta, Cargando, EstadoVacio, Paginacion, ConfirmarEliminar, EncabezadoPagina
└─ pages/                 Una carpeta por módulo
   ├─ Login, Dashboard, NoEncontrado
   ├─ usuarios/   horarios/   academico/   matricula/   calificaciones/
```

## División del trabajo

| Integrante | Rama | Responsabilidad |
| --- | --- | --- |
| Fabricio | `fabricio-frontend` | Base del proyecto, login/logout, rutas protegidas, layout, componentes compartidos, Dashboard, Usuarios y Horarios |
| David | `david-academico` | Carreras, Cursos, Períodos y Grupos |
| Gabriel | `gabriel-matricula-calificaciones` | Matrículas, Evaluaciones y Calificaciones |

## Matriz de pantallas y endpoints

| Pantalla | Acción en la interfaz | Método | Ruta REST |
| --- | --- | --- | --- |
| Login | Iniciar sesión | POST | `/api/token/` |
| (todas) | Cargar usuario y rol al entrar | GET | `/api/usuarios/perfil/` |
| Dashboard | Indicador de cursos | GET | `/api/academico/cursos/?page_size=1` |
| Dashboard | Indicador de grupos | GET | `/api/academico/grupos/?page_size=1` |
| Dashboard | Indicador de matrículas activas | GET | `/api/matricula/?estado=MATRICULADO&page_size=1` |
| Dashboard | Indicador de horarios | GET | `/api/horarios/?page_size=1` |
| Usuarios | Ver mi perfil | GET | `/api/usuarios/perfil/` |
| Usuarios | Ver todos los perfiles (admin) | GET | `/api/usuarios/perfiles/` |
| Horarios | Listar con filtros y paginación | GET | `/api/horarios/?grupo=&dia=&aula=&page=&page_size=` |
| Horarios | Cargar grupos para los selectores | GET | `/api/academico/grupos/?page_size=50` |
| Horarios | Crear horario | POST | `/api/horarios/` |
| Horarios | Editar horario | PATCH | `/api/horarios/{id}/` |
| Horarios | Eliminar horario | DELETE | `/api/horarios/{id}/` |

*(David y Gabriel agregan aquí las filas de sus módulos.)*

## Matriz de perfiles y permisos (módulos de esta rama)

| Pantalla / acción | Admin | Profesor | Estudiante |
| --- | --- | --- | --- |
| Dashboard | Ve todo | Ve datos de sus grupos | Ve sus matrículas y horarios |
| Usuarios: mi perfil | Sí | Sí | Sí |
| Usuarios: todos los perfiles | Sí | 403 | 403 |
| Horarios: consultar | Todos | Los de sus grupos | Los de sus grupos matriculados |
| Horarios: crear / editar / eliminar | Sí | Solo en grupos que imparte (si no, 403) | No (403) |

## Escenarios de prueba manual (parte de Fabricio)

| # | Escenario | Pasos | Resultado esperado |
| --- | --- | --- | --- |
| 1 | Login correcto | Entrar con un usuario válido | Redirige al Dashboard y muestra nombre y rol arriba |
| 2 | Login incorrecto | Contraseña equivocada | Alerta "Usuario o contraseña incorrectos" |
| 3 | Ruta protegida sin sesión | Abrir `/horarios` sin haber iniciado sesión | Redirige a `/login` y, después de entrar, vuelve a `/horarios` |
| 4 | Logout | Botón "Salir" | Borra el token de `localStorage` y vuelve al login |
| 5 | Token inválido (401) | Cambiar el token en `localStorage` y recargar | Vuelve al login con el aviso de sesión expirada |
| 6 | Acceso denegado (403) | Como estudiante, en Usuarios presionar "Intentar consultar perfiles" | Alerta "Error 403: No tiene permisos..." |
| 7 | Validación en el cliente | Guardar un horario vacío | Mensajes debajo de cada campo obligatorio |
| 8 | Validación del servidor | Crear un horario en un aula ocupada a la misma hora | Django responde 400 y el error aparece debajo del campo Aula |
| 9 | Crear horario | Llenar el formulario y guardar | Alerta de éxito y la tabla se actualiza |
| 10 | Editar horario | Botón Editar | El formulario se precarga; al actualizar se refleja en la tabla |
| 11 | Eliminar horario | Botón Eliminar y confirmar | Pide confirmación, elimina y actualiza la tabla |
| 12 | Filtros combinables | Filtrar por grupo y día a la vez | Solo aparecen los horarios que cumplen ambos filtros (filtrado en el backend) |
| 13 | Paginación | Con más de 10 horarios, cambiar de página | Se piden `page=2` al backend y cambia el texto "Mostrando..." |
| 14 | Diseño adaptable | Abrir en celular o con la ventana angosta | El menú se oculta y se abre con el botón ☰ |
| 15 | Servidor apagado | Detener Django y recargar una lista | Mensaje "No se pudo conectar con el servidor" |

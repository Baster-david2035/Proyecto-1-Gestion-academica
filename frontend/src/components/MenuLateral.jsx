import { NavLink } from 'react-router-dom'

// Opciones del menú agrupadas por módulo.
// Todos los roles ven el menú; lo que cada uno puede hacer lo decide Django.
const SECCIONES = [
  {
    titulo: 'General',
    enlaces: [
      { ruta: '/', texto: 'Dashboard' },
      { ruta: '/usuarios', texto: 'Usuarios' },
    ],
  },
  {
    titulo: 'Académico',
    enlaces: [
      { ruta: '/academico/carreras', texto: 'Carreras' },
      { ruta: '/academico/cursos', texto: 'Cursos' },
      { ruta: '/academico/periodos', texto: 'Períodos' },
      { ruta: '/academico/grupos', texto: 'Grupos' },
    ],
  },
  {
    titulo: 'Matrícula',
    enlaces: [{ ruta: '/matriculas', texto: 'Matrículas' }],
  },
  {
    titulo: 'Calificaciones',
    enlaces: [
      { ruta: '/evaluaciones', texto: 'Evaluaciones' },
      { ruta: '/calificaciones', texto: 'Calificaciones' },
    ],
  },
  {
    titulo: 'Horarios',
    enlaces: [{ ruta: '/horarios', texto: 'Horarios' }],
  },
]

export default function MenuLateral({ onNavegar }) {
  return (
    <nav>
      {SECCIONES.map((seccion) => (
        <div key={seccion.titulo}>
          <div className="titulo-seccion">{seccion.titulo}</div>
          <ul className="nav flex-column">
            {seccion.enlaces.map((enlace) => (
              <li className="nav-item" key={enlace.ruta}>
                {/* "end" evita que Dashboard quede activo en todas las rutas */}
                <NavLink className="nav-link py-1" to={enlace.ruta} end onClick={onNavegar}>
                  {enlace.texto}
                </NavLink>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  )
}

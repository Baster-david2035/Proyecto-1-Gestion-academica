import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import EncabezadoPagina from '../components/EncabezadoPagina'
import { useAuth } from '../context/AuthContext'
import { api } from '../services/api'

// Accesos directos a los cinco módulos
const MODULOS = [
  { titulo: 'Usuarios', descripcion: 'Perfil y roles del sistema', ruta: '/usuarios' },
  { titulo: 'Académico', descripcion: 'Carreras, cursos, períodos y grupos', ruta: '/academico/cursos' },
  { titulo: 'Matrícula', descripcion: 'Solicitudes y estado de matrícula', ruta: '/matriculas' },
  { titulo: 'Calificaciones', descripcion: 'Evaluaciones y notas por grupo', ruta: '/evaluaciones' },
  { titulo: 'Horarios', descripcion: 'Días, horas y aulas de cada grupo', ruta: '/horarios' },
]

// Para contar registros pedimos solo 1 resultado y usamos el "count" que devuelve Django
async function contar(ruta, parametros = {}) {
  const datos = await api.get(ruta, { ...parametros, page_size: 1 })
  return datos.count
}

export default function Dashboard() {
  const { perfil, esEstudiante, esProfesor } = useAuth()
  const [indicadores, setIndicadores] = useState([])
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    let activo = true

    async function cargarIndicadores() {
      // Los textos cambian según el rol, porque Django solo devuelve lo que cada uno puede ver
      const consultas = [
        { titulo: 'Cursos registrados', promesa: contar('/academico/cursos/') },
        {
          titulo: esProfesor ? 'Grupos (todos)' : 'Grupos ofertados',
          promesa: contar('/academico/grupos/'),
        },
        {
          titulo: esEstudiante ? 'Mis matrículas activas' : 'Matrículas activas',
          promesa: contar('/matricula/', { estado: 'MATRICULADO' }),
        },
        {
          titulo: esEstudiante ? 'Mis horarios' : esProfesor ? 'Horarios de mis grupos' : 'Horarios programados',
          promesa: contar('/horarios/'),
        },
      ]

      // allSettled: si una consulta falla (ej. 403) las demás igual se muestran
      const resultados = await Promise.allSettled(consultas.map((c) => c.promesa))
      if (!activo) return

      setIndicadores(
        consultas.map((consulta, i) => ({
          titulo: consulta.titulo,
          valor: resultados[i].status === 'fulfilled' ? resultados[i].value : null,
          error: resultados[i].status === 'rejected' ? resultados[i].reason.message : '',
        })),
      )
      setCargando(false)
    }

    cargarIndicadores()
    return () => {
      activo = false
    }
  }, [esEstudiante, esProfesor])

  const nombre = perfil?.user?.first_name || perfil?.user?.username || ''

  return (
    <>
      <EncabezadoPagina
        titulo={`Bienvenido${nombre ? `, ${nombre}` : ''}`}
        descripcion="Resumen general del sistema con datos reales de la API."
      />

      <div className="row g-3 mb-4">
        {(cargando ? [1, 2, 3, 4] : indicadores).map((indicador, i) => (
          <div className="col-6 col-lg-3" key={i}>
            <div className="card h-100 shadow-sm">
              <div className="card-body">
                {cargando ? (
                  <div className="placeholder-glow">
                    <span className="placeholder col-8 mb-2" />
                    <span className="placeholder col-4 placeholder-lg" />
                  </div>
                ) : (
                  <>
                    <div className="text-secondary small">{indicador.titulo}</div>
                    {indicador.valor !== null ? (
                      <div className="indicador">{indicador.valor}</div>
                    ) : (
                      <div className="small text-danger mt-2" title={indicador.error}>
                        No disponible
                      </div>
                    )}
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      <h2 className="h5 mb-3">Módulos</h2>
      <div className="row g-3">
        {MODULOS.map((modulo) => (
          <div className="col-sm-6 col-xl-4" key={modulo.ruta}>
            <Link to={modulo.ruta} className="card h-100 text-decoration-none shadow-sm">
              <div className="card-body">
                <h3 className="h6 text-primary mb-1">{modulo.titulo}</h3>
                <p className="text-secondary small mb-0">{modulo.descripcion}</p>
              </div>
            </Link>
          </div>
        ))}
      </div>
    </>
  )
}

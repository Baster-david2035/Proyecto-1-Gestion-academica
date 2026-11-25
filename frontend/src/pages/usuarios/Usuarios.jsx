import { useEffect, useState } from 'react'
import Alerta from '../../components/Alerta'
import Cargando from '../../components/Cargando'
import EncabezadoPagina from '../../components/EncabezadoPagina'
import EstadoVacio from '../../components/EstadoVacio'
import { useAuth } from '../../context/AuthContext'
import { api } from '../../services/api'

const COLORES_ROL = {
  ADMIN: 'danger',
  PROFESOR: 'primary',
  ESTUDIANTE: 'success',
}

// Este módulo es solo de consulta: el backend no tiene endpoints para crear,
// editar o borrar usuarios (eso se hace en /admin de Django)
export default function Usuarios() {
  const { perfil, esAdmin } = useAuth()

  const [perfiles, setPerfiles] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState('')

  async function cargarPerfiles() {
    try {
      setCargando(true)
      setError('')
      const datos = await api.get('/usuarios/perfiles/')
      setPerfiles(datos)
    } catch (err) {
      // Aquí se ve el 403 cuando un profesor o estudiante intenta entrar
      setError(`${err.status ? `Error ${err.status}: ` : ''}${err.message}`)
      setPerfiles([])
    } finally {
      setCargando(false)
    }
  }

  // Solo el admin carga la lista automáticamente
  useEffect(() => {
    if (esAdmin) cargarPerfiles()
  }, [esAdmin])

  const usuario = perfil?.user

  return (
    <>
      <EncabezadoPagina titulo="Usuarios" descripcion="Información de la cuenta y perfiles del sistema." />

      <div className="card shadow-sm mb-4">
        <div className="card-header bg-white fw-semibold">Mi perfil</div>
        <div className="card-body">
          {!perfil ? (
            <Alerta tipo="warning" mensaje="Su usuario no tiene un perfil registrado en el sistema." />
          ) : (
            <dl className="row mb-0">
              <dt className="col-sm-3">Usuario</dt>
              <dd className="col-sm-9">{usuario.username}</dd>
              <dt className="col-sm-3">Nombre</dt>
              <dd className="col-sm-9">{`${usuario.first_name} ${usuario.last_name}`.trim() || '—'}</dd>
              <dt className="col-sm-3">Correo</dt>
              <dd className="col-sm-9">{usuario.email || '—'}</dd>
              <dt className="col-sm-3">Rol</dt>
              <dd className="col-sm-9">
                <span className={`badge text-bg-${COLORES_ROL[perfil.rol] || 'secondary'}`}>{perfil.rol}</span>
              </dd>
              <dt className="col-sm-3">Teléfono</dt>
              <dd className="col-sm-9 mb-0">{perfil.telefono || '—'}</dd>
            </dl>
          )}
        </div>
      </div>

      <div className="card shadow-sm">
        <div className="card-header bg-white d-flex justify-content-between align-items-center">
          <span className="fw-semibold">Todos los perfiles</span>
          {esAdmin && (
            <button className="btn btn-outline-secondary btn-sm" onClick={cargarPerfiles} disabled={cargando}>
              Actualizar
            </button>
          )}
        </div>
        <div className="card-body">
          {!esAdmin && (
            <>
              <p className="text-secondary">
                Esta lista es exclusiva del administrador. Puede intentar consultarla para comprobar que el
                servidor rechaza la solicitud.
              </p>
              <button className="btn btn-outline-danger btn-sm mb-3" onClick={cargarPerfiles} disabled={cargando}>
                Intentar consultar perfiles
              </button>
            </>
          )}

          <Alerta tipo="danger" mensaje={error} />

          {cargando && <Cargando texto="Consultando perfiles..." />}

          {esAdmin && !cargando && !error && perfiles.length === 0 && (
            <EstadoVacio mensaje="No hay perfiles registrados." />
          )}

          {!cargando && perfiles.length > 0 && (
            <div className="table-responsive">
              <table className="table table-hover align-middle mb-0">
                <thead>
                  <tr>
                    <th>Usuario</th>
                    <th>Nombre</th>
                    <th>Correo</th>
                    <th>Rol</th>
                    <th>Teléfono</th>
                  </tr>
                </thead>
                <tbody>
                  {perfiles.map((p) => (
                    <tr key={p.id}>
                      <td>{p.user.username}</td>
                      <td>{`${p.user.first_name} ${p.user.last_name}`.trim() || '—'}</td>
                      <td>{p.user.email || '—'}</td>
                      <td>
                        <span className={`badge text-bg-${COLORES_ROL[p.rol] || 'secondary'}`}>{p.rol}</span>
                      </td>
                      <td>{p.telefono || '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </>
  )
}

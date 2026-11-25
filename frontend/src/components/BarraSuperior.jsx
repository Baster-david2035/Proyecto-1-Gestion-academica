import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const NOMBRES_ROL = {
  ADMIN: 'Administrador',
  PROFESOR: 'Profesor',
  ESTUDIANTE: 'Estudiante',
}

export default function BarraSuperior({ onAlternarMenu }) {
  const { perfil, rol, cerrarSesion } = useAuth()

  const usuario = perfil?.user
  const nombre = usuario
    ? `${usuario.first_name} ${usuario.last_name}`.trim() || usuario.username
    : 'Usuario'

  return (
    <nav className="navbar navbar-dark bg-primary px-3 flex-nowrap">
      <div className="d-flex align-items-center gap-2 text-truncate">
        {/* Este botón solo se ve en celular para abrir el menú */}
        <button
          className="navbar-toggler d-md-none"
          type="button"
          aria-label="Abrir menú"
          onClick={onAlternarMenu}
        >
          <span className="navbar-toggler-icon" />
        </button>
        <Link className="navbar-brand mb-0" to="/">
          Gestión Académica
        </Link>
      </div>

      <div className="d-flex align-items-center gap-3 text-white flex-shrink-0">
        <div className="text-end d-none d-sm-block">
          <div className="fw-semibold lh-1">{nombre}</div>
          <small className="opacity-75">{NOMBRES_ROL[rol] || 'Sin perfil'}</small>
        </div>
        <button className="btn btn-outline-light btn-sm text-nowrap" onClick={() => cerrarSesion()}>
          Salir
        </button>
      </div>
    </nav>
  )
}

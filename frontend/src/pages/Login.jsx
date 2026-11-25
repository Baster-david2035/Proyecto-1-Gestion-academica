import { useState } from 'react'
import { Navigate, useLocation, useNavigate } from 'react-router-dom'
import Alerta from '../components/Alerta'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { iniciarSesion, estaAutenticado } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()

  const [formulario, setFormulario] = useState({ username: '', password: '' })
  const [error, setError] = useState('')
  const [procesando, setProcesando] = useState(false)

  // Mensaje que llega cuando la sesión expiró (lo manda AuthContext)
  const mensajeSesion = location.state?.mensaje

  // Si ya inició sesión no tiene sentido mostrar el login
  if (estaAutenticado) return <Navigate to="/" replace />

  function manejarCambio(e) {
    setFormulario({ ...formulario, [e.target.name]: e.target.value })
  }

  async function manejarEnvio(e) {
    e.preventDefault()
    setError('')

    // Validación rápida antes de llamar a la API
    if (!formulario.username.trim() || !formulario.password) {
      setError('Debe escribir el usuario y la contraseña.')
      return
    }

    try {
      setProcesando(true)
      await iniciarSesion(formulario.username.trim(), formulario.password)
      // Volvemos a la página que quería ver antes del login, o al dashboard
      navigate(location.state?.desde || '/', { replace: true })
    } catch (err) {
      setError(
        err.status === 400
          ? 'Usuario o contraseña incorrectos.'
          : err.message,
      )
    } finally {
      setProcesando(false)
    }
  }

  return (
    <div className="container min-vh-100 d-flex align-items-center justify-content-center">
      <div className="card shadow-sm w-100" style={{ maxWidth: 400 }}>
        <div className="card-body p-4">
          <h1 className="h4 text-center mb-1">Gestión Académica</h1>
          <p className="text-center text-secondary mb-4">Inicie sesión para continuar</p>

          <Alerta tipo="warning" mensaje={mensajeSesion} />
          <Alerta tipo="danger" mensaje={error} />

          <form onSubmit={manejarEnvio} noValidate>
            <div className="mb-3">
              <label htmlFor="username" className="form-label">
                Usuario
              </label>
              <input
                id="username"
                name="username"
                className="form-control"
                autoComplete="username"
                value={formulario.username}
                onChange={manejarCambio}
                required
              />
            </div>
            <div className="mb-4">
              <label htmlFor="password" className="form-label">
                Contraseña
              </label>
              <input
                id="password"
                name="password"
                type="password"
                className="form-control"
                autoComplete="current-password"
                value={formulario.password}
                onChange={manejarCambio}
                required
              />
            </div>
            <button type="submit" className="btn btn-primary w-100" disabled={procesando}>
              {procesando ? 'Ingresando...' : 'Iniciar sesión'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

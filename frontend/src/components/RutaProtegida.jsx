import { Navigate, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import Cargando from './Cargando'

// Si no hay sesión, mandamos al login y recordamos a qué página quería ir
export default function RutaProtegida() {
  const { estaAutenticado, cargando } = useAuth()
  const location = useLocation()

  if (cargando) return <Cargando texto="Verificando sesión..." />

  if (!estaAutenticado) {
    return <Navigate to="/login" replace state={{ desde: location.pathname }} />
  }

  return <Outlet />
}

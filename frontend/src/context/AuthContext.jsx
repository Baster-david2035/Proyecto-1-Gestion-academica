import { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  borrarToken,
  consultarMiPerfil,
  guardarToken,
  iniciarSesionApi,
  obtenerToken,
} from '../services/api'

// El contexto nos deja compartir la sesión entre todas las páginas
// sin tener que pasar props por todos lados
const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const navigate = useNavigate()
  const [token, setToken] = useState(obtenerToken())
  const [perfil, setPerfil] = useState(null)
  const [cargando, setCargando] = useState(Boolean(obtenerToken()))

  // Cuando hay token, pedimos el perfil para saber quién es y qué rol tiene
  useEffect(() => {
    // Sin token no hay nada que cargar (cerrarSesion ya limpia el perfil)
    if (!token) return

    let activo = true
    async function cargarPerfil() {
      try {
        setCargando(true)
        const datos = await consultarMiPerfil()
        if (activo) setPerfil(datos)
      } catch {
        // Si el perfil no carga (por ejemplo 401), dejamos la sesión sin perfil;
        // el 401 ya se encarga de sacar al usuario con el evento sesion-expirada
        if (activo) setPerfil(null)
      } finally {
        if (activo) setCargando(false)
      }
    }
    cargarPerfil()

    return () => {
      activo = false
    }
  }, [token])

  const cerrarSesion = useCallback(
    (mensaje = '') => {
      // Ojo: el backend no tiene endpoint para revocar el token,
      // así que aquí solo lo borramos del navegador
      borrarToken()
      setToken(null)
      setPerfil(null)
      navigate('/login', { replace: true, state: mensaje ? { mensaje } : null })
    },
    [navigate],
  )

  // api.js lanza este evento cuando Django responde 401
  useEffect(() => {
    function manejarSesionExpirada() {
      cerrarSesion('Su sesión expiró o el token ya no es válido. Inicie sesión de nuevo.')
    }
    window.addEventListener('sesion-expirada', manejarSesionExpirada)
    return () => window.removeEventListener('sesion-expirada', manejarSesionExpirada)
  }, [cerrarSesion])

  async function iniciarSesion(username, password) {
    const nuevoToken = await iniciarSesionApi(username, password)
    guardarToken(nuevoToken)
    setToken(nuevoToken)
  }

  const rol = perfil?.rol ?? null

  const valor = {
    token,
    perfil,
    rol,
    cargando,
    estaAutenticado: Boolean(token),
    esAdmin: rol === 'ADMIN',
    esProfesor: rol === 'PROFESOR',
    esEstudiante: rol === 'ESTUDIANTE',
    iniciarSesion,
    cerrarSesion,
  }

  return <AuthContext.Provider value={valor}>{children}</AuthContext.Provider>
}

// Hook para usar la sesión en cualquier componente: const { perfil } = useAuth()
export function useAuth() {
  return useContext(AuthContext)
}

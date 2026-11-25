// Aquí centralizamos todas las llamadas a la API de Django.
// Ningún componente debería escribir la URL completa del backend.

const API_URL = import.meta.env.VITE_API_URL || '/api'
const TOKEN_KEY = 'gestion_academica_token'

// ---------- Token en localStorage (igual que en clase) ----------

export function guardarToken(token) {
  localStorage.setItem(TOKEN_KEY, token)
}

export function obtenerToken() {
  return localStorage.getItem(TOKEN_KEY)
}

export function borrarToken() {
  localStorage.removeItem(TOKEN_KEY)
}

// ---------- Errores ----------

// Error propio para saber el código HTTP y los errores por campo que manda Django
export class ErrorApi extends Error {
  constructor(mensaje, status, detalles = null) {
    super(mensaje)
    this.status = status
    this.detalles = detalles
  }
}

const MENSAJES_POR_ESTADO = {
  400: 'Hay datos que no son válidos. Revise el formulario.',
  401: 'Su sesión no es válida o expiró. Inicie sesión de nuevo.',
  403: 'No tiene permisos para realizar esta acción.',
  404: 'El registro no existe o no tiene acceso a él.',
  409: 'La operación entra en conflicto con otro registro.',
  500: 'Ocurrió un error en el servidor. Intente más tarde.',
}

// Django puede responder {error: "..."}, {detail: "..."} o {campo: ["..."]}.
// Esta función saca un texto entendible de cualquiera de esos formatos.
function sacarMensaje(datos, status) {
  if (!datos || typeof datos !== 'object') {
    return MENSAJES_POR_ESTADO[status] || `Error inesperado (${status}).`
  }
  if (typeof datos.error === 'string') return datos.error
  if (typeof datos.detail === 'string') return datos.detail

  const mensajes = []
  for (const [campo, valor] of Object.entries(datos)) {
    const texto = Array.isArray(valor) ? valor.join(' ') : String(valor)
    if (campo === 'non_field_errors') {
      mensajes.push(texto)
    } else {
      mensajes.push(`${campo}: ${texto}`)
    }
  }
  return mensajes.length > 0 ? mensajes.join(' | ') : MENSAJES_POR_ESTADO[status]
}

// ---------- Función base para hacer peticiones ----------

async function peticion(ruta, opciones = {}) {
  const headers = { ...opciones.headers }
  const token = obtenerToken()

  if (token) {
    // DRF usa el prefijo "Token", no "Bearer"
    headers.Authorization = `Token ${token}`
  }
  if (opciones.body) {
    headers['Content-Type'] = 'application/json'
  }

  let respuesta
  try {
    respuesta = await fetch(`${API_URL}${ruta}`, { ...opciones, headers })
  } catch {
    // fetch solo falla aquí cuando no hay conexión con el servidor
    throw new ErrorApi(
      'No se pudo conectar con el servidor. Revise que Django esté encendido.',
      0,
    )
  }

  // DELETE responde 204 sin contenido
  if (respuesta.status === 204) return null

  let datos = null
  try {
    datos = await respuesta.json()
  } catch {
    datos = null
  }

  if (!respuesta.ok) {
    if (respuesta.status === 401) {
      // El token ya no sirve: lo borramos y avisamos al AuthContext
      borrarToken()
      window.dispatchEvent(new Event('sesion-expirada'))
    }
    throw new ErrorApi(sacarMensaje(datos, respuesta.status), respuesta.status, datos)
  }

  return datos
}

// Arma "?page=1&grupo=2" ignorando los filtros vacíos
export function armarQuery(parametros = {}) {
  const query = new URLSearchParams()
  for (const [clave, valor] of Object.entries(parametros)) {
    if (valor !== '' && valor !== null && valor !== undefined) {
      query.append(clave, valor)
    }
  }
  const texto = query.toString()
  return texto ? `?${texto}` : ''
}

// Atajos para cada método HTTP
export const api = {
  get: (ruta, parametros) => peticion(`${ruta}${armarQuery(parametros)}`),
  post: (ruta, datos) => peticion(ruta, { method: 'POST', body: JSON.stringify(datos) }),
  patch: (ruta, datos) => peticion(ruta, { method: 'PATCH', body: JSON.stringify(datos) }),
  eliminar: (ruta) => peticion(ruta, { method: 'DELETE' }),
}

// Las listas paginadas vienen como {count, results}; otras vienen como arreglo
export function obtenerResultados(datos) {
  return Array.isArray(datos) ? datos : datos?.results ?? []
}

// ---------- Autenticación ----------

export async function iniciarSesionApi(username, password) {
  const datos = await peticion('/token/', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  })
  if (!datos?.token) {
    throw new ErrorApi('El servidor no devolvió un token.', 500)
  }
  return datos.token
}

export function consultarMiPerfil() {
  return api.get('/usuarios/perfil/')
}

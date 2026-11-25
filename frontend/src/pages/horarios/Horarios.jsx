import { useEffect, useState } from 'react'
import Alerta from '../../components/Alerta'
import Cargando from '../../components/Cargando'
import ConfirmarEliminar from '../../components/ConfirmarEliminar'
import EncabezadoPagina from '../../components/EncabezadoPagina'
import EstadoVacio from '../../components/EstadoVacio'
import Paginacion from '../../components/Paginacion'
import { useAuth } from '../../context/AuthContext'
import { api, obtenerResultados } from '../../services/api'
import { DIAS, nombreDia, nombreGrupo } from './constantes'
import HorarioForm from './HorarioForm'
import TablaHorarios from './TablaHorarios'

const TAMANO_PAGINA = 10
const FILTROS_VACIOS = { grupo: '', dia: '', aula: '' }

export default function Horarios() {
  const { perfil, esAdmin, esProfesor } = useAuth()

  // Datos de la tabla
  const [horarios, setHorarios] = useState([])
  const [total, setTotal] = useState(0)
  const [pagina, setPagina] = useState(1)
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [mensaje, setMensaje] = useState('')

  // Filtros: los del formulario y los que ya se aplicaron a la consulta
  const [filtrosFormulario, setFiltrosFormulario] = useState(FILTROS_VACIOS)
  const [filtros, setFiltros] = useState(FILTROS_VACIOS)

  // Grupos para los selects (relación Horario -> Grupo)
  const [grupos, setGrupos] = useState([])

  // Formulario y eliminación
  const [mostrarFormulario, setMostrarFormulario] = useState(false)
  const [horarioEditando, setHorarioEditando] = useState(null)
  const [horarioEliminar, setHorarioEliminar] = useState(null)
  const [eliminando, setEliminando] = useState(false)
  const [recargar, setRecargar] = useState(0)

  // Solo admin y profesores pueden crear/editar; igual Django lo vuelve a revisar
  const puedeGestionar = esAdmin || esProfesor

  // Cargar grupos una sola vez
  useEffect(() => {
    let activo = true
    async function cargarGrupos() {
      try {
        const datos = await api.get('/academico/grupos/', { page_size: 50 })
        if (activo) setGrupos(obtenerResultados(datos))
      } catch {
        // Si no se pueden cargar, los filtros simplemente quedan sin opciones
        if (activo) setGrupos([])
      }
    }
    cargarGrupos()
    return () => {
      activo = false
    }
  }, [])

  // Cada vez que cambia la página, los filtros o se guarda algo, volvemos a consultar
  useEffect(() => {
    let activo = true
    async function cargarHorarios() {
      try {
        setCargando(true)
        setError('')
        const datos = await api.get('/horarios/', {
          ...filtros,
          page: pagina,
          page_size: TAMANO_PAGINA,
        })
        if (!activo) return
        setHorarios(obtenerResultados(datos))
        setTotal(datos.count ?? 0)
      } catch (err) {
        if (activo) setError(err.message)
      } finally {
        if (activo) setCargando(false)
      }
    }
    cargarHorarios()
    return () => {
      activo = false
    }
  }, [filtros, pagina, recargar])

  function manejarCambioFiltro(e) {
    setFiltrosFormulario({ ...filtrosFormulario, [e.target.name]: e.target.value })
  }

  function aplicarFiltros(e) {
    e.preventDefault()
    setPagina(1)
    setFiltros({ ...filtrosFormulario, aula: filtrosFormulario.aula.trim() })
  }

  function limpiarFiltros() {
    setFiltrosFormulario(FILTROS_VACIOS)
    setFiltros(FILTROS_VACIOS)
    setPagina(1)
  }

  function abrirNuevo() {
    setHorarioEditando(null)
    setMostrarFormulario(true)
    setMensaje('')
  }

  function abrirEdicion(horario) {
    setHorarioEditando(horario)
    setMostrarFormulario(true)
    setMensaje('')
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  function cerrarFormulario() {
    setMostrarFormulario(false)
    setHorarioEditando(null)
  }

  // POST si es nuevo, PATCH si está editando. Los errores los maneja HorarioForm.
  async function guardarHorario(datos) {
    if (horarioEditando) {
      await api.patch(`/horarios/${horarioEditando.id}/`, datos)
      setMensaje('Horario actualizado correctamente.')
    } else {
      await api.post('/horarios/', datos)
      setMensaje('Horario creado correctamente.')
    }
    cerrarFormulario()
    setRecargar((valor) => valor + 1)
  }

  async function confirmarEliminacion() {
    try {
      setEliminando(true)
      await api.eliminar(`/horarios/${horarioEliminar.id}/`)
      setMensaje('Horario eliminado correctamente.')
      // Si borramos el último de la página, regresamos una página
      if (horarios.length === 1 && pagina > 1) {
        setPagina(pagina - 1)
      } else {
        setRecargar((valor) => valor + 1)
      }
    } catch (err) {
      setError(err.message)
    } finally {
      setEliminando(false)
      setHorarioEliminar(null)
    }
  }

  // El profesor solo puede asignar horarios a los grupos que imparte
  const gruposFormulario = esProfesor ? grupos.filter((g) => g.profesor === perfil?.user?.id) : grupos

  const hayFiltros = Object.values(filtros).some((valor) => valor !== '')

  return (
    <>
      <EncabezadoPagina titulo="Horarios" descripcion="Días, horas y aulas asignadas a cada grupo.">
        {puedeGestionar && !mostrarFormulario && (
          <button className="btn btn-primary" onClick={abrirNuevo}>
            Nuevo horario
          </button>
        )}
      </EncabezadoPagina>

      <Alerta tipo="success" mensaje={mensaje} onCerrar={() => setMensaje('')} />

      {mostrarFormulario && (
        <HorarioForm
          // key hace que el formulario se reinicie al cambiar de registro
          key={horarioEditando?.id ?? 'nuevo'}
          horario={horarioEditando}
          grupos={gruposFormulario}
          onGuardar={guardarHorario}
          onCancelar={cerrarFormulario}
        />
      )}

      {/* Filtros combinables: se envían al backend como ?grupo=&dia=&aula= */}
      <form className="card shadow-sm mb-3" onSubmit={aplicarFiltros}>
        <div className="card-body">
          <div className="row g-2 align-items-end">
            <div className="col-md-4">
              <label htmlFor="filtro-grupo" className="form-label small">
                Grupo
              </label>
              <select
                id="filtro-grupo"
                name="grupo"
                className="form-select form-select-sm"
                value={filtrosFormulario.grupo}
                onChange={manejarCambioFiltro}
              >
                <option value="">Todos</option>
                {grupos.map((grupo) => (
                  <option key={grupo.id} value={grupo.id}>
                    {nombreGrupo(grupo)}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-6 col-md-2">
              <label htmlFor="filtro-dia" className="form-label small">
                Día
              </label>
              <select
                id="filtro-dia"
                name="dia"
                className="form-select form-select-sm"
                value={filtrosFormulario.dia}
                onChange={manejarCambioFiltro}
              >
                <option value="">Todos</option>
                {DIAS.map((dia) => (
                  <option key={dia.valor} value={dia.valor}>
                    {dia.texto}
                  </option>
                ))}
              </select>
            </div>
            <div className="col-6 col-md-3">
              <label htmlFor="filtro-aula" className="form-label small">
                Aula
              </label>
              <input
                id="filtro-aula"
                name="aula"
                className="form-control form-control-sm"
                placeholder="Ej: Lab"
                value={filtrosFormulario.aula}
                onChange={manejarCambioFiltro}
              />
            </div>
            <div className="col-md-3 d-flex gap-2">
              <button type="submit" className="btn btn-primary btn-sm flex-fill">
                Filtrar
              </button>
              <button type="button" className="btn btn-outline-secondary btn-sm flex-fill" onClick={limpiarFiltros}>
                Limpiar
              </button>
            </div>
          </div>
        </div>
      </form>

      <Alerta tipo="danger" mensaje={error} onCerrar={() => setError('')} />

      {cargando ? (
        <Cargando texto="Cargando horarios..." />
      ) : horarios.length === 0 ? (
        <EstadoVacio
          mensaje={
            hayFiltros
              ? `No hay horarios que coincidan con los filtros${filtros.dia ? ` (${nombreDia(filtros.dia)})` : ''}.`
              : 'Todavía no hay horarios registrados.'
          }
        />
      ) : (
        <>
          <TablaHorarios
            horarios={horarios}
            puedeGestionar={puedeGestionar}
            onEditar={abrirEdicion}
            onEliminar={setHorarioEliminar}
          />
          <Paginacion pagina={pagina} tamano={TAMANO_PAGINA} total={total} onCambiar={setPagina} />
        </>
      )}

      <ConfirmarEliminar
        visible={Boolean(horarioEliminar)}
        mensaje={
          horarioEliminar &&
          `¿Desea eliminar el horario de ${horarioEliminar.grupo_detalle} el ${nombreDia(horarioEliminar.dia)}?`
        }
        procesando={eliminando}
        onConfirmar={confirmarEliminacion}
        onCancelar={() => setHorarioEliminar(null)}
      />
    </>
  )
}

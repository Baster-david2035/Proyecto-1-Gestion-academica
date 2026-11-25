import { useState } from 'react'
import Alerta from '../../components/Alerta'
import { DIAS, horaCorta, nombreGrupo } from './constantes'

const FORMULARIO_VACIO = {
  grupo: '',
  dia: 'LUN',
  hora_inicio: '',
  hora_fin: '',
  aula: '',
}

// Formulario para crear o editar un horario.
// Si recibe "horario" está editando y precarga sus valores.
export default function HorarioForm({ horario, grupos, onGuardar, onCancelar }) {
  const [formulario, setFormulario] = useState(
    horario
      ? {
          grupo: String(horario.grupo),
          dia: horario.dia,
          hora_inicio: horaCorta(horario.hora_inicio),
          hora_fin: horaCorta(horario.hora_fin),
          aula: horario.aula,
        }
      : FORMULARIO_VACIO,
  )
  const [errores, setErrores] = useState({})
  const [errorGeneral, setErrorGeneral] = useState('')
  const [procesando, setProcesando] = useState(false)

  function manejarCambio(e) {
    setFormulario({ ...formulario, [e.target.name]: e.target.value })
  }

  // Validaciones del lado del cliente; Django igual vuelve a validar todo
  function validar() {
    const nuevos = {}
    if (!formulario.grupo) nuevos.grupo = 'Seleccione un grupo.'
    if (!formulario.hora_inicio) nuevos.hora_inicio = 'Indique la hora de inicio.'
    if (!formulario.hora_fin) nuevos.hora_fin = 'Indique la hora de finalización.'
    if (formulario.hora_inicio && formulario.hora_fin && formulario.hora_fin <= formulario.hora_inicio) {
      nuevos.hora_fin = 'La hora de finalización debe ser posterior a la de inicio.'
    }
    if (!formulario.aula.trim()) nuevos.aula = 'El aula es obligatoria.'
    return nuevos
  }

  async function manejarEnvio(e) {
    e.preventDefault()
    setErrorGeneral('')

    const nuevosErrores = validar()
    setErrores(nuevosErrores)
    if (Object.keys(nuevosErrores).length > 0) return

    try {
      setProcesando(true)
      await onGuardar({
        ...formulario,
        grupo: Number(formulario.grupo),
        aula: formulario.aula.trim(),
      })
    } catch (err) {
      // Si Django devuelve errores por campo ({aula: ["..."]}) los ponemos debajo de cada input
      if (err.status === 400 && err.detalles && typeof err.detalles === 'object') {
        const deServidor = {}
        for (const [campo, mensajes] of Object.entries(err.detalles)) {
          deServidor[campo] = Array.isArray(mensajes) ? mensajes.join(' ') : String(mensajes)
        }
        setErrores(deServidor)
        setErrorGeneral(deServidor.non_field_errors || 'El servidor rechazó los datos. Revise los campos marcados.')
      } else {
        setErrorGeneral(err.message)
      }
    } finally {
      setProcesando(false)
    }
  }

  // Clase de Bootstrap para pintar en rojo el input con error
  const claseInput = (campo, base = 'form-control') => `${base} ${errores[campo] ? 'is-invalid' : ''}`

  return (
    <div className="card shadow-sm mb-4">
      <div className="card-header bg-white fw-semibold">{horario ? 'Editar horario' : 'Nuevo horario'}</div>
      <div className="card-body">
        <Alerta tipo="danger" mensaje={errorGeneral} />

        <form onSubmit={manejarEnvio} noValidate>
          <div className="row g-3">
            <div className="col-md-6">
              <label htmlFor="grupo" className="form-label">
                Grupo *
              </label>
              <select
                id="grupo"
                name="grupo"
                className={claseInput('grupo', 'form-select')}
                value={formulario.grupo}
                onChange={manejarCambio}
                required
              >
                <option value="">Seleccione...</option>
                {grupos.map((grupo) => (
                  <option key={grupo.id} value={grupo.id}>
                    {nombreGrupo(grupo)}
                  </option>
                ))}
              </select>
              <div className="invalid-feedback">{errores.grupo}</div>
            </div>

            <div className="col-md-6">
              <label htmlFor="dia" className="form-label">
                Día *
              </label>
              <select
                id="dia"
                name="dia"
                className={claseInput('dia', 'form-select')}
                value={formulario.dia}
                onChange={manejarCambio}
                required
              >
                {DIAS.map((dia) => (
                  <option key={dia.valor} value={dia.valor}>
                    {dia.texto}
                  </option>
                ))}
              </select>
              <div className="invalid-feedback">{errores.dia}</div>
            </div>

            <div className="col-6 col-md-4">
              <label htmlFor="hora_inicio" className="form-label">
                Hora de inicio *
              </label>
              <input
                id="hora_inicio"
                name="hora_inicio"
                type="time"
                className={claseInput('hora_inicio')}
                value={formulario.hora_inicio}
                onChange={manejarCambio}
                required
              />
              <div className="invalid-feedback">{errores.hora_inicio}</div>
            </div>

            <div className="col-6 col-md-4">
              <label htmlFor="hora_fin" className="form-label">
                Hora de fin *
              </label>
              <input
                id="hora_fin"
                name="hora_fin"
                type="time"
                className={claseInput('hora_fin')}
                value={formulario.hora_fin}
                onChange={manejarCambio}
                required
              />
              <div className="invalid-feedback">{errores.hora_fin}</div>
            </div>

            <div className="col-md-4">
              <label htmlFor="aula" className="form-label">
                Aula *
              </label>
              <input
                id="aula"
                name="aula"
                className={claseInput('aula')}
                value={formulario.aula}
                onChange={manejarCambio}
                maxLength={20}
                placeholder="Ej: Lab-01"
                required
              />
              <div className="invalid-feedback">{errores.aula}</div>
            </div>
          </div>

          <div className="d-flex gap-2 mt-4">
            <button type="submit" className="btn btn-primary" disabled={procesando}>
              {procesando ? 'Guardando...' : horario ? 'Actualizar' : 'Guardar'}
            </button>
            <button type="button" className="btn btn-outline-secondary" onClick={onCancelar} disabled={procesando}>
              Cancelar
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

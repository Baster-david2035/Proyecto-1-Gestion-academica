import { horaCorta, nombreDia } from './constantes'

// Tabla de horarios con botones de editar y eliminar por fila
export default function TablaHorarios({ horarios, puedeGestionar, onEditar, onEliminar }) {
  return (
    <div className="table-responsive">
      <table className="table table-hover align-middle bg-white mb-0">
        <thead className="table-light">
          <tr>
            <th>Grupo</th>
            <th>Día</th>
            <th>Horario</th>
            <th>Aula</th>
            {puedeGestionar && <th className="text-end">Acciones</th>}
          </tr>
        </thead>
        <tbody>
          {horarios.map((horario) => (
            <tr key={horario.id}>
              <td>{horario.grupo_detalle}</td>
              <td>{nombreDia(horario.dia)}</td>
              <td>
                {horaCorta(horario.hora_inicio)} – {horaCorta(horario.hora_fin)}
              </td>
              <td>{horario.aula}</td>
              {puedeGestionar && (
                <td className="text-end text-nowrap">
                  <button className="btn btn-outline-primary btn-sm me-2" onClick={() => onEditar(horario)}>
                    Editar
                  </button>
                  <button className="btn btn-outline-danger btn-sm" onClick={() => onEliminar(horario)}>
                    Eliminar
                  </button>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

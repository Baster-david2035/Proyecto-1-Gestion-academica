// Ventana para confirmar antes de borrar algo.
// Se muestra solo cuando "visible" es true.
export default function ConfirmarEliminar({ visible, mensaje, procesando, onConfirmar, onCancelar }) {
  if (!visible) return null

  return (
    <>
      <div className="modal d-block" tabIndex="-1" role="dialog">
        <div className="modal-dialog modal-dialog-centered">
          <div className="modal-content">
            <div className="modal-header">
              <h5 className="modal-title">Confirmar eliminación</h5>
              <button type="button" className="btn-close" onClick={onCancelar} disabled={procesando} />
            </div>
            <div className="modal-body">
              <p className="mb-0">{mensaje}</p>
              <small className="text-secondary">Esta acción no se puede deshacer.</small>
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={onCancelar} disabled={procesando}>
                Cancelar
              </button>
              <button className="btn btn-danger" onClick={onConfirmar} disabled={procesando}>
                {procesando ? 'Eliminando...' : 'Sí, eliminar'}
              </button>
            </div>
          </div>
        </div>
      </div>
      <div className="modal-backdrop show" />
    </>
  )
}

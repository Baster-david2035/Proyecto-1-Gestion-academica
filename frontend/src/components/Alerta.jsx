// Alerta de Bootstrap reutilizable. tipo: success, danger, warning, info
export default function Alerta({ tipo = 'info', mensaje, onCerrar }) {
  if (!mensaje) return null

  return (
    <div className={`alert alert-${tipo} d-flex justify-content-between align-items-start`} role="alert">
      <span>{mensaje}</span>
      {onCerrar && (
        <button type="button" className="btn-close ms-3" aria-label="Cerrar" onClick={onCerrar} />
      )}
    </div>
  )
}

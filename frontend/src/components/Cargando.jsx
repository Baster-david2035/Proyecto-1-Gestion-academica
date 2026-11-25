export default function Cargando({ texto = 'Cargando...' }) {
  return (
    <div className="d-flex align-items-center gap-2 text-secondary py-4">
      <div className="spinner-border spinner-border-sm" role="status" />
      <span>{texto}</span>
    </div>
  )
}

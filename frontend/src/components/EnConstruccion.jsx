import EncabezadoPagina from './EncabezadoPagina'

// Página temporal para los módulos que todavía están en otra rama.
// Cada responsable reemplaza el archivo de su página y esto desaparece.
export default function EnConstruccion({ titulo, responsable, rama }) {
  return (
    <>
      <EncabezadoPagina titulo={titulo} />
      <div className="alert alert-secondary">
        Esta pantalla está en desarrollo por <strong>{responsable}</strong> en la rama{' '}
        <code>{rama}</code>.
      </div>
    </>
  )
}

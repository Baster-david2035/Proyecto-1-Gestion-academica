export default function EstadoVacio({ mensaje = 'No hay registros para mostrar.' }) {
  return (
    <div className="text-center text-secondary border rounded bg-white py-5">
      <p className="mb-0">{mensaje}</p>
    </div>
  )
}

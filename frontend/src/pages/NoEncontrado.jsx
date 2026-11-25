import { Link } from 'react-router-dom'

export default function NoEncontrado() {
  return (
    <div className="text-center py-5">
      <h1 className="display-6">Página no encontrada</h1>
      <p className="text-secondary">La dirección que escribió no existe en el sistema.</p>
      <Link to="/" className="btn btn-primary">
        Volver al dashboard
      </Link>
    </div>
  )
}

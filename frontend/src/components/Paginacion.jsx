// Paginación que usa los parámetros page y page_size del backend.
// total viene del campo "count" que devuelve Django.
export default function Paginacion({ pagina, tamano, total, onCambiar }) {
  const totalPaginas = Math.max(1, Math.ceil(total / tamano))
  if (total === 0) return null

  const desde = (pagina - 1) * tamano + 1
  const hasta = Math.min(pagina * tamano, total)

  // Mostramos como máximo 5 números alrededor de la página actual
  const inicio = Math.max(1, Math.min(pagina - 2, totalPaginas - 4))
  const fin = Math.min(totalPaginas, inicio + 4)
  const numeros = []
  for (let i = inicio; i <= fin; i++) numeros.push(i)

  return (
    <div className="d-flex flex-column flex-sm-row justify-content-between align-items-center gap-2 mt-3">
      <small className="text-secondary">
        Mostrando {desde}–{hasta} de {total}
      </small>
      <nav aria-label="Paginación">
        <ul className="pagination pagination-sm mb-0">
          <li className={`page-item ${pagina === 1 ? 'disabled' : ''}`}>
            <button className="page-link" onClick={() => onCambiar(pagina - 1)}>
              Anterior
            </button>
          </li>
          {numeros.map((numero) => (
            <li key={numero} className={`page-item ${numero === pagina ? 'active' : ''}`}>
              <button className="page-link" onClick={() => onCambiar(numero)}>
                {numero}
              </button>
            </li>
          ))}
          <li className={`page-item ${pagina === totalPaginas ? 'disabled' : ''}`}>
            <button className="page-link" onClick={() => onCambiar(pagina + 1)}>
              Siguiente
            </button>
          </li>
        </ul>
      </nav>
    </div>
  )
}

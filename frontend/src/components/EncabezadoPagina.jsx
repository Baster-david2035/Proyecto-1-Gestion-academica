// Título de cada pantalla con un espacio a la derecha para botones (ej: "Nuevo")
export default function EncabezadoPagina({ titulo, descripcion, children }) {
  return (
    <div className="d-flex flex-column flex-md-row justify-content-between align-items-md-center gap-2 mb-4">
      <div>
        <h1 className="h3 mb-1">{titulo}</h1>
        {descripcion && <p className="text-secondary mb-0">{descripcion}</p>}
      </div>
      {children && <div className="d-flex gap-2">{children}</div>}
    </div>
  )
}

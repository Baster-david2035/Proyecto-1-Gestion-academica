import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import BarraSuperior from './BarraSuperior'
import MenuLateral from './MenuLateral'

// Estructura general: barra arriba, menú a la izquierda y el contenido
// de cada módulo en el centro (Outlet cambia sin recargar la página)
export default function Layout() {
  const [menuAbierto, setMenuAbierto] = useState(false)

  return (
    <>
      <BarraSuperior onAlternarMenu={() => setMenuAbierto(!menuAbierto)} />
      <div className="container-fluid">
        <div className="row">
          <aside
            className={`col-md-3 col-lg-2 menu-lateral p-3 ${menuAbierto ? 'd-block' : 'd-none'} d-md-block`}
          >
            <MenuLateral onNavegar={() => setMenuAbierto(false)} />
          </aside>
          <main className="col-md-9 col-lg-10 p-3 p-md-4">
            <Outlet />
          </main>
        </div>
      </div>
    </>
  )
}

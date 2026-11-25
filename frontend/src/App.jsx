import { Route, Routes } from 'react-router-dom'
import Layout from './components/Layout'
import RutaProtegida from './components/RutaProtegida'
import Dashboard from './pages/Dashboard'
import Login from './pages/Login'
import NoEncontrado from './pages/NoEncontrado'
import Usuarios from './pages/usuarios/Usuarios'
import Horarios from './pages/horarios/Horarios'
import Carreras from './pages/academico/Carreras'
import Cursos from './pages/academico/Cursos'
import Periodos from './pages/academico/Periodos'
import Grupos from './pages/academico/Grupos'
import Matriculas from './pages/matricula/Matriculas'
import Evaluaciones from './pages/calificaciones/Evaluaciones'
import Calificaciones from './pages/calificaciones/Calificaciones'

// Todas las rutas de la app. Las privadas van dentro de RutaProtegida,
// que manda al login si no hay token.
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />

      <Route element={<RutaProtegida />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/usuarios" element={<Usuarios />} />

          {/* Módulo académico (David) */}
          <Route path="/academico/carreras" element={<Carreras />} />
          <Route path="/academico/cursos" element={<Cursos />} />
          <Route path="/academico/periodos" element={<Periodos />} />
          <Route path="/academico/grupos" element={<Grupos />} />

          {/* Matrícula y calificaciones (Gabriel) */}
          <Route path="/matriculas" element={<Matriculas />} />
          <Route path="/evaluaciones" element={<Evaluaciones />} />
          <Route path="/calificaciones" element={<Calificaciones />} />

          <Route path="/horarios" element={<Horarios />} />
          <Route path="*" element={<NoEncontrado />} />
        </Route>
      </Route>
    </Routes>
  )
}

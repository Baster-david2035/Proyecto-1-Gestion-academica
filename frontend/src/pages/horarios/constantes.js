// Mismos días que define el modelo HorarioGrupo en Django
export const DIAS = [
  { valor: 'LUN', texto: 'Lunes' },
  { valor: 'MAR', texto: 'Martes' },
  { valor: 'MIE', texto: 'Miércoles' },
  { valor: 'JUE', texto: 'Jueves' },
  { valor: 'VIE', texto: 'Viernes' },
  { valor: 'SAB', texto: 'Sábado' },
]

export function nombreDia(valor) {
  return DIAS.find((d) => d.valor === valor)?.texto ?? valor
}

// Texto para mostrar un grupo en los selects
export function nombreGrupo(grupo) {
  return `${grupo.curso_nombre} - G${grupo.numero_grupo} (${grupo.periodo_nombre})`
}

// Django manda "08:00:00"; para mostrar y para el input time usamos "08:00"
export function horaCorta(hora) {
  return hora ? hora.slice(0, 5) : ''
}

import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `rounded-md px-3 py-2 text-sm font-medium transition ${
    isActive
      ? 'bg-violet-100 text-violet-800'
      : 'text-slate-700 hover:bg-slate-100'
  }`

export function AppNav() {
  return (
    <nav
      aria-label="Основная навигация"
      className="flex flex-wrap gap-2 border-b border-slate-200 bg-white px-4 py-3"
    >
      <NavLink to="/" end className={linkClass}>
        Написание тест-кейсов
      </NavLink>
      <NavLink to="/settings" className={linkClass}>
        Настройки
      </NavLink>
    </nav>
  )
}

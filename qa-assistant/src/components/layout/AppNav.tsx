import { NavLink } from 'react-router-dom'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `app-shell__nav-link rounded-md px-3 py-2 text-sm font-medium transition ${
    isActive
      ? 'bg-violet-100 text-violet-800'
      : 'text-slate-700 hover:bg-slate-100'
  }`

export function AppNav() {
  return (
    <nav
      aria-label="Основная навигация"
      className="app-shell__nav border-b border-slate-200 bg-white"
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

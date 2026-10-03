import { NavLink } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import { Button } from '../ui/Button'

const linkClass = ({ isActive }: { isActive: boolean }) =>
  `app-shell__nav-link rounded-md px-3 py-2 text-sm font-medium transition-colors ${
    isActive
      ? 'bg-violet-100 text-violet-800'
      : 'text-slate-700 hover:bg-slate-100'
  }`

export function AppNav() {
  const { configured, user, signOut } = useAuth()

  return (
    <nav
      aria-label="Основная навигация"
      className="app-shell__nav flex flex-wrap items-center border-b border-slate-200 bg-white"
    >
      <div className="flex flex-wrap items-center gap-1">
        <NavLink to="/" end className={linkClass}>
          Написание тест-кейсов
        </NavLink>
        <NavLink to="/settings" className={linkClass}>
          Настройки
        </NavLink>
      </div>
      {configured && user ? (
        <div className="ml-auto flex items-center gap-2 px-2 py-1">
          <span
            className="max-w-[12rem] truncate text-xs text-slate-600"
            title={user.email ?? undefined}
          >
            {user.email}
          </span>
          <Button
            type="button"
            variant="secondary"
            className="!w-auto"
            onClick={() => void signOut()}
          >
            Выйти
          </Button>
        </div>
      ) : null}
    </nav>
  )
}

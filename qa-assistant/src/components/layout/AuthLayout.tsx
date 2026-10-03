import { Outlet } from 'react-router-dom'
import { Header } from './Header'

/**
 * Отдельный каркас для входа/регистрации — без общих вкладок AppNav.
 */
export function AuthLayout() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <Header />
      <main className="app-shell__main">
        <Outlet />
      </main>
    </div>
  )
}

import { Outlet } from 'react-router-dom'
import { AppNav } from './AppNav'
import { Header } from './Header'

/**
 * Адаптивный каркас приложения: header → nav → main.
 * Отступы и max-width задаются media queries в `index.css` (классы `app-shell__*`).
 */
export function AppLayout() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <Header />
      <AppNav />
      <main className="app-shell__main">
        <Outlet />
      </main>
    </div>
  )
}

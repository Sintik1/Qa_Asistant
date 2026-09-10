import { Outlet } from 'react-router-dom'
import { AppNav } from './AppNav'
import { Header } from './Header'

export function AppLayout() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <Header />
      <AppNav />
      <main className="mx-auto max-w-3xl px-4 py-8">
        <Outlet />
      </main>
    </div>
  )
}

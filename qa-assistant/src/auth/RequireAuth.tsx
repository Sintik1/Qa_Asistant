import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'

/**
 * When Supabase is configured, require a session.
 * Without env keys (local mock / Vitest) — pass through.
 */
export function RequireAuth() {
  const { configured, loading, user } = useAuth()

  if (!configured) {
    return <Outlet />
  }

  if (loading) {
    return (
      <p className="text-sm text-slate-600" role="status">
        Проверка сессии…
      </p>
    )
  }

  if (!user) {
    return <Navigate to="/auth" replace />
  }

  return <Outlet />
}

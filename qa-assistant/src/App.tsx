import { Suspense, lazy } from 'react'
import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import { MetrikaRouteTracker } from './analytics/MetrikaRouteTracker'
import { AuthProvider } from './auth/AuthContext'
import { RequireAuth } from './auth/RequireAuth'
import { AppLayout } from './components/layout/AppLayout'
import { AuthLayout } from './components/layout/AuthLayout'
import { HomePage } from './pages/HomePage'

const AuthPage = lazy(() =>
  import('./pages/AuthPage').then((m) => ({ default: m.AuthPage })),
)
const AuthCallbackPage = lazy(() =>
  import('./pages/AuthCallbackPage').then((m) => ({ default: m.AuthCallbackPage })),
)
const ChatPage = lazy(() =>
  import('./pages/ChatPage').then((m) => ({ default: m.ChatPage })),
)
const SettingsPage = lazy(() =>
  import('./pages/SettingsPage').then((m) => ({ default: m.SettingsPage })),
)

function RouteFallback() {
  return (
    <p className="p-6 text-sm text-slate-600" role="status">
      Загрузка…
    </p>
  )
}

function routerBasename(): string | undefined {
  const base = import.meta.env.BASE_URL || '/'
  const trimmed = base.replace(/\/$/, '')
  return trimmed === '' ? undefined : trimmed
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter basename={routerBasename()}>
        <MetrikaRouteTracker />
        <Suspense fallback={<RouteFallback />}>
          <Routes>
            <Route element={<AuthLayout />}>
              <Route path="auth" element={<AuthPage />} />
              <Route path="auth/callback" element={<AuthCallbackPage />} />
            </Route>

            <Route element={<RequireAuth />}>
              <Route element={<AppLayout />}>
                <Route index element={<HomePage />} />
                <Route path="chat" element={<ChatPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App

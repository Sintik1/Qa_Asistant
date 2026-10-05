import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { trackGoal } from '../analytics/metrika'
import { useAuth } from '../auth/AuthContext'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { PageHeader } from '../components/ui/PageHeader'

/**
 * OAuth redirect target:
 * - Google (Supabase PKCE): session restored via detectSessionInUrl
 * - Yandex (Flask): tokens in URL hash → setSession
 */
export function AuthCallbackPage() {
  const { configured, applySessionTokens, user, loading } = useAuth()
  const navigate = useNavigate()
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const oauthError = params.get('oauth_error')
    const oauthMessage = params.get('oauth_message')
    if (oauthError) {
      setError(oauthMessage || oauthError)
      return
    }

    const hash = window.location.hash.replace(/^#/, '')
    if (hash) {
      const hashParams = new URLSearchParams(hash)
      const access = hashParams.get('access_token')
      const refresh = hashParams.get('refresh_token')
      if (access && refresh) {
        void (async () => {
          const message = await applySessionTokens(access, refresh)
          // Clear tokens from address bar
          window.history.replaceState(null, '', '/auth/callback')
          if (message) {
            setError(message)
            return
          }
          trackGoal('auth_login', { method: 'oauth' })
          navigate('/', { replace: true })
        })()
        return
      }
    }

    // Google / email: wait for supabase session from URL
    if (!loading && user) {
      trackGoal('auth_login', { method: 'oauth' })
      navigate('/', { replace: true })
    }
  }, [applySessionTokens, loading, navigate, user])

  if (!configured) {
    return <Navigate to="/auth" replace />
  }

  return (
    <div>
      <PageHeader
        title="Завершение входа"
        description="Обрабатываем ответ OAuth-провайдера…"
      />
      {error ? (
        <div className="max-w-xl space-y-3">
          <ErrorMessage message={error} />
          <a className="text-sm text-violet-700 underline" href="/auth">
            Вернуться ко входу
          </a>
        </div>
      ) : (
        <p className="text-sm text-slate-600" role="status">
          Подождите…
        </p>
      )}
    </div>
  )
}

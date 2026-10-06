import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { trackGoal } from '../analytics/metrika'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { PageHeader } from '../components/ui/PageHeader'
import { INPUT_CLASS } from '../utils/formStyles'
import { apiBaseUrl, isApiConfigured } from '../api/client'

type Mode = 'login' | 'signup'

/**
 * Email/password + OAuth2 (Google via Supabase Auth, Yandex via Flask).
 */
export function AuthPage() {
  const { configured, loading, user, signIn, signUp, signInWithOAuth } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [oauthBusy, setOauthBusy] = useState<'google' | 'yandex' | null>(null)

  if (!loading && user) {
    return <Navigate to="/" replace />
  }

  if (!configured) {
    return (
      <div>
        <PageHeader
          title="Вход"
          description="Supabase Auth не настроен. Заполните VITE_SUPABASE_URL и VITE_SUPABASE_ANON_KEY."
        />
      </div>
    )
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setInfo(null)
    setSubmitting(true)
    try {
      if (mode === 'login') {
        const message = await signIn(email.trim(), password)
        if (message) {
          setError(message)
          return
        }
        trackGoal('auth_login', { method: 'password' })
        navigate('/', { replace: true })
        return
      }

      const message = await signUp(email.trim(), password)
      if (message) {
        setError(message)
        return
      }
      trackGoal('auth_signup', { method: 'password' })
      setInfo(
        'Регистрация принята. Если включено подтверждение email — проверьте почту, иначе можно сразу войти.',
      )
      setMode('login')
    } finally {
      setSubmitting(false)
    }
  }

  const handleOAuth = async (provider: 'google' | 'yandex') => {
    setError(null)
    setInfo(null)
    setOauthBusy(provider)
    try {
      if (provider === 'yandex' && !isApiConfigured()) {
        setError('Для Yandex OAuth задайте VITE_API_BASE_URL (Flask).')
        return
      }
      trackGoal('auth_oauth_start', { provider })
      const message = await signInWithOAuth(provider)
      if (message) setError(message)
    } finally {
      setOauthBusy(null)
    }
  }

  return (
    <div>
      <PageHeader
        title={mode === 'login' ? 'Вход' : 'Регистрация'}
        description="Email/пароль или OAuth2 (Google через Supabase / Yandex через Flask)."
      />

      <div className="mb-6 flex w-full max-w-xl flex-col gap-2">
        <Button
          type="button"
          variant="secondary"
          disabled={submitting || loading || oauthBusy !== null}
          onClick={() => void handleOAuth('google')}
        >
          {oauthBusy === 'google' ? 'Переход к Google…' : 'Войти через Google'}
        </Button>
        <Button
          type="button"
          variant="secondary"
          disabled={submitting || loading || oauthBusy !== null}
          onClick={() => void handleOAuth('yandex')}
        >
          {oauthBusy === 'yandex' ? 'Переход к Yandex…' : 'Войти через Yandex'}
        </Button>
        <p className="text-xs text-slate-500">
          Google: Supabase Auth Provider. Yandex:{' '}
          {isApiConfigured()
            ? `Flask → ${apiBaseUrl()}`
            : 'нужен VITE_API_BASE_URL (сейчас не задан).'}
        </p>
      </div>

      <p className="mb-4 max-w-xl text-sm text-slate-500">или email и пароль</p>

      <form className="w-full max-w-xl space-y-4" onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label htmlFor="auth-email" className="block text-sm font-medium">
            Email
          </label>
          <input
            id="auth-email"
            type="email"
            autoComplete="email"
            required
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            className={INPUT_CLASS}
            placeholder="you@example.com"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="auth-password" className="block text-sm font-medium">
            Пароль
          </label>
          <input
            id="auth-password"
            type="password"
            autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
            required
            minLength={6}
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            className={INPUT_CLASS}
            placeholder="Минимум 6 символов"
          />
        </div>

        {error ? <ErrorMessage message={error} /> : null}
        {info ? (
          <p className="text-sm text-green-700" role="status">
            {info}
          </p>
        ) : null}

        <div className="app-actions flex flex-wrap gap-2">
          <Button type="submit" disabled={submitting || loading || oauthBusy !== null}>
            {mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={submitting || oauthBusy !== null}
            onClick={() => {
              setError(null)
              setInfo(null)
              setMode((current) => (current === 'login' ? 'signup' : 'login'))
            }}
          >
            {mode === 'login' ? 'Создать аккаунт' : 'Уже есть аккаунт'}
          </Button>
        </div>
      </form>
    </div>
  )
}

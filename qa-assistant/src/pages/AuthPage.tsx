import { useState, type FormEvent } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { Button } from '../components/ui/Button'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { PageHeader } from '../components/ui/PageHeader'
import { INPUT_CLASS } from '../utils/formStyles'

type Mode = 'login' | 'signup'

/**
 * Регистрация / вход через Supabase Auth (email + password).
 */
export function AuthPage() {
  const { configured, loading, user, signIn, signUp } = useAuth()
  const navigate = useNavigate()
  const [mode, setMode] = useState<Mode>('login')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [info, setInfo] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

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
        navigate('/', { replace: true })
        return
      }

      const message = await signUp(email.trim(), password)
      if (message) {
        setError(message)
        return
      }
      setInfo(
        'Регистрация принята. Если включено подтверждение email — проверьте почту, иначе можно сразу войти.',
      )
      setMode('login')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div>
      <PageHeader
        title={mode === 'login' ? 'Вход' : 'Регистрация'}
        description="Аутентификация через Supabase Auth (email и пароль)."
      />

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
          <Button type="submit" disabled={submitting || loading}>
            {mode === 'login' ? 'Войти' : 'Зарегистрироваться'}
          </Button>
          <Button
            type="button"
            variant="secondary"
            disabled={submitting}
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

import { useState, type FormEvent } from 'react'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { ERROR_MESSAGES } from '../utils/constants'

/**
 * Settings screen from TZ §3.5 — API token configuration.
 * Not present as a separate frame in the current Figma file;
 * required by MUST HAVE acceptance criteria.
 */
export function SettingsPage() {
  const [token, setToken] = useState('')
  const [savedHint, setSavedHint] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSave = (event: FormEvent) => {
    event.preventDefault()
    if (!token.trim()) {
      setError(ERROR_MESSAGES.MISSING_TOKEN)
      setSavedHint(null)
      return
    }
    // Token persistence via backend/.env is out of scope for structure step
    setError(null)
    setSavedHint('Токен принят локально (сохранение на сервере — позже).')
  }

  return (
    <div>
      <PageHeader
        title="Настройки"
        description="Управление API-токеном доступа к ИИ-агенту."
      />

      <form className="max-w-xl space-y-4" onSubmit={handleSave}>
        <div className="space-y-2">
          <label htmlFor="api-token" className="block text-sm font-medium">
            API-токен
          </label>
          <input
            id="api-token"
            type="password"
            autoComplete="off"
            value={token}
            onChange={(event) => setToken(event.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-200"
            placeholder="Введите токен"
          />
        </div>

        {error ? (
          <ErrorMessage message={error} actionLabel="Изменить токен" />
        ) : null}
        {savedHint ? (
          <p className="text-sm text-green-700" role="status">
            {savedHint}
          </p>
        ) : null}

        <Button type="submit" variant="secondary" className="w-auto">
          Сохранить токен
        </Button>
      </form>
    </div>
  )
}

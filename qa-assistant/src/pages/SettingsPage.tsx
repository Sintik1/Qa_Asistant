import { useState, type FormEvent } from 'react'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { API_TOKEN_STORAGE_KEY, ERROR_MESSAGES } from '../utils/constants'

/**
 * Экран настроек по ТЗ §3.5 — API-токен (mock в localStorage до бэкенда).
 */
export function SettingsPage() {
  const [token, setToken] = useState(
    () => localStorage.getItem(API_TOKEN_STORAGE_KEY) ?? '',
  )
  const [savedHint, setSavedHint] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleSave = (event: FormEvent) => {
    event.preventDefault()
    if (!token.trim()) {
      setError(ERROR_MESSAGES.MISSING_TOKEN_ON_SETTINGS)
      setSavedHint(null)
      localStorage.removeItem(API_TOKEN_STORAGE_KEY)
      return
    }
    localStorage.setItem(API_TOKEN_STORAGE_KEY, token.trim())
    setError(null)
    setSavedHint('Токен сохранён локально (mock). Бэкенд/.env — на следующем этапе.')
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

        {error ? <ErrorMessage message={error} /> : null}
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

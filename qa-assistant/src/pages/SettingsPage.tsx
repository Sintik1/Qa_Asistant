import { useEffect, useState, type FormEvent } from 'react'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { useSettingsApi } from '../hooks/useSettingsApi'
import { API_TOKEN_STORAGE_KEY, ERROR_MESSAGES } from '../utils/constants'
import { INPUT_CLASS } from '../utils/formStyles'
import { isApiConfigured } from '../api'

/**
 * Экран настроек по ТЗ §3.5 — API-токен + chunk settings через Flask.
 * Сам Leopold/Ollama token хранится в server `.env`; UI ставит `has_api_token`.
 */
export function SettingsPage() {
  const settingsApi = useSettingsApi()
  const [token, setToken] = useState(
    () => localStorage.getItem(API_TOKEN_STORAGE_KEY) ?? '',
  )
  const [savedHint, setSavedHint] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (settingsApi.error) setError(settingsApi.error)
  }, [settingsApi.error])

  const handleSave = async (event: FormEvent) => {
    event.preventDefault()
    const trimmed = token.trim()
    if (!trimmed) {
      setError(ERROR_MESSAGES.MISSING_TOKEN_ON_SETTINGS)
      setSavedHint(null)
      localStorage.removeItem(API_TOKEN_STORAGE_KEY)
      try {
        await settingsApi.setHasApiToken(false)
      } catch {
        /* error already in hook */
      }
      return
    }

    localStorage.setItem(API_TOKEN_STORAGE_KEY, trimmed)
    setError(null)

    try {
      if (isApiConfigured()) {
        await settingsApi.setHasApiToken(true)
        await settingsApi.saveChunkSettings(settingsApi.chunkSettings)
        setSavedHint(
          'Настройки сохранены на сервере. Токен ИИ задаётся в `.env` бэкенда (QA_ASISTANT_API_TOKEN); флаг has_api_token обновлён.',
        )
      } else {
        setSavedHint(
          'Токен сохранён локально. Задайте VITE_API_BASE_URL для синхронизации с API.',
        )
      }
    } catch {
      setSavedHint(null)
    }
  }

  return (
    <div>
      <PageHeader
        title="Настройки"
        description="Управление API-токеном доступа к ИИ-агенту и параметрами чанков."
      />

      <form className="w-full max-w-xl space-y-4" onSubmit={(e) => void handleSave(e)}>
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
            className={INPUT_CLASS}
            placeholder="Введите токен"
          />
        </div>

        {settingsApi.loading ? (
          <p className="text-sm text-slate-500" role="status">
            Загрузка настроек с сервера…
          </p>
        ) : null}

        {error ? <ErrorMessage message={error} /> : null}
        {savedHint ? (
          <p className="text-sm text-green-700" role="status">
            {savedHint}
          </p>
        ) : null}

        <div className="app-actions">
          <Button type="submit" variant="secondary">
            Сохранить токен
          </Button>
        </div>
      </form>
    </div>
  )
}

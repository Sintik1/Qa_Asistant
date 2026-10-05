import { useEffect, useState, type FormEvent } from 'react'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { useSettingsApi } from '../hooks/useSettingsApi'
import { API_TOKEN_STORAGE_KEY } from '../utils/constants'
import { isApiConfigured } from '../api'

/**
 * Настройки: флаг has_api_token на сервере.
 * Секрет Leopold/Ollama хранится только в server `.env` — не в localStorage / не в UI.
 */
export function SettingsPage() {
  const settingsApi = useSettingsApi()
  const [savedHint, setSavedHint] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    // B3a: purge legacy mock-era token from browser storage.
    localStorage.removeItem(API_TOKEN_STORAGE_KEY)
  }, [])

  useEffect(() => {
    if (settingsApi.error) setError(settingsApi.error)
  }, [settingsApi.error])

  const handleMarkConfigured = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setSavedHint(null)
    if (!isApiConfigured()) {
      setError(
        'Не задан VITE_API_BASE_URL. Укажите URL Flask API в qa-assistant/.env.local',
      )
      return
    }
    try {
      await settingsApi.setHasApiToken(true)
      setSavedHint(
        'Флаг has_api_token=true сохранён. Сам токен ИИ задайте в `.env` бэкенда (QA_ASISTANT_API_TOKEN / Leopold).',
      )
    } catch {
      setSavedHint(null)
    }
  }

  const handleClearFlag = async () => {
    setError(null)
    setSavedHint(null)
    if (!isApiConfigured()) {
      setError(
        'Не задан VITE_API_BASE_URL. Укажите URL Flask API в qa-assistant/.env.local',
      )
      return
    }
    try {
      await settingsApi.setHasApiToken(false)
      setSavedHint('Флаг has_api_token сброшен на сервере.')
    } catch {
      setSavedHint(null)
    }
  }

  return (
    <div>
      <PageHeader
        title="Настройки"
        description="Токен ИИ хранится только на сервере (.env). Здесь — статус флага и параметры чанков на Home."
      />

      <form
        className="w-full max-w-xl space-y-4"
        onSubmit={(e) => void handleMarkConfigured(e)}
      >
        <div className="space-y-2 rounded-md border border-slate-200 bg-slate-50 p-4 text-sm text-slate-700">
          <p>
            Статус на сервере:{' '}
            <strong>
              {settingsApi.loading
                ? '…'
                : settingsApi.hasApiToken
                  ? 'токен отмечен как настроенный'
                  : 'токен не отмечен'}
            </strong>
          </p>
          <p className="text-slate-600">
            Не вводите секрет в браузер. Задайте его в корневом{' '}
            <code className="text-xs">.env</code> и отметьте флаг ниже.
          </p>
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

        <div className="app-actions flex flex-wrap gap-2">
          <Button type="submit" variant="secondary">
            Отметить токен настроенным
          </Button>
          <Button type="button" variant="secondary" onClick={() => void handleClearFlag()}>
            Сбросить флаг
          </Button>
        </div>
      </form>
    </div>
  )
}

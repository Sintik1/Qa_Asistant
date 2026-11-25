import { useEffect, useState } from 'react'
import { getAiProvider, setAiProvider, type AiProviderName } from '../../api/settings'

export function AiProviderSwitch() {
  const [provider, setProvider] = useState<AiProviderName | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    void getAiProvider()
      .then((status) => {
        if (!cancelled) setProvider(status.provider)
      })
      .catch(() => {
        if (!cancelled) setError('Не удалось прочитать провайдер ИИ')
      })
    return () => {
      cancelled = true
    }
  }, [])

  async function choose(next: AiProviderName) {
    if (busy || next === provider) return
    setBusy(true)
    setError(null)
    try {
      const status = await setAiProvider(next)
      setProvider(status.provider)
    } catch {
      setError('Не удалось переключить модель')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="flex items-center gap-1" role="group" aria-label="Провайдер ИИ">
      <button
        type="button"
        className={`rounded-md px-2.5 py-1.5 text-xs font-medium ${
          provider === 'ollama' ? 'bg-violet-700 text-white' : 'bg-slate-100 text-slate-700'
        }`}
        aria-pressed={provider === 'ollama'}
        disabled={busy}
        onClick={() => void choose('ollama')}
      >
        Локально
      </button>
      <button
        type="button"
        className={`rounded-md px-2.5 py-1.5 text-xs font-medium ${
          provider === 'leopold' ? 'bg-violet-700 text-white' : 'bg-slate-100 text-slate-700'
        }`}
        aria-pressed={provider === 'leopold'}
        disabled={busy}
        onClick={() => void choose('leopold')}
      >
        Leopold
      </button>
      {error ? <span className="text-xs text-red-700">{error}</span> : null}
    </div>
  )
}

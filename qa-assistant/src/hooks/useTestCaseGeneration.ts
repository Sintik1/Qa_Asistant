import { useCallback, useRef, useState } from 'react'
import type {
  ChunkSettings,
  GenerationResult,
  GenerationStatus,
  SelectedFileInfo,
} from '../types'
import { ERROR_MESSAGES, NOTIFY_AFTER_MS } from '../utils/constants'
import { downloadCsv } from '../utils/csvExport'
import {
  DEFAULT_CHUNK_SETTINGS,
  LONG_DOCUMENT_BYTES,
  mockGenerateTestCases,
} from '../utils/mockGeneration'

interface UseTestCaseGenerationResult {
  status: GenerationStatus
  progressLabel: string | null
  error: string | null
  result: GenerationResult | null
  chunkSettings: ChunkSettings
  setChunkSettings: (next: ChunkSettings) => void
  showChunkPanel: boolean
  setShowChunkPanel: (open: boolean) => void
  warning: string | null
  clearWarning: () => void
  generate: (file: SelectedFileInfo) => Promise<void>
  downloadResultCsv: () => void
  clearError: () => void
}

/**
 * Mock-поток генерации: прогресс извлечения → генерация → опциональное уведомление.
 */
export function useTestCaseGeneration(): UseTestCaseGenerationResult {
  const [status, setStatus] = useState<GenerationStatus>('idle')
  const [progressLabel, setProgressLabel] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [chunkSettings, setChunkSettings] = useState<ChunkSettings>(
    DEFAULT_CHUNK_SETTINGS,
  )
  const [showChunkPanel, setShowChunkPanel] = useState(false)
  const [warning, setWarning] = useState<string | null>(null)
  const startedAtRef = useRef<number>(0)
  const resultRef = useRef<GenerationResult | null>(null)

  const clearWarning = useCallback(() => setWarning(null), [])
  const clearError = useCallback(() => setError(null), [])

  const maybeNotify = useCallback((next: GenerationResult) => {
    const elapsed = Date.now() - startedAtRef.current
    if (elapsed < NOTIFY_AFTER_MS || !document.hidden) return
    if (!('Notification' in window)) return

    const show = () => {
      const n = new Notification(ERROR_MESSAGES.GENERATION_DONE_NOTIFY)
      n.onclick = () => {
        window.focus()
        downloadCsv(next.cases, next.generatedAt)
        n.close()
      }
    }

    if (Notification.permission === 'granted') {
      show()
    } else if (Notification.permission !== 'denied') {
      void Notification.requestPermission().then((perm) => {
        if (perm === 'granted') show()
      })
    }
  }, [])

  const runGeneration = useCallback(
    async (file: SelectedFileInfo, settings: ChunkSettings) => {
      startedAtRef.current = Date.now()
      setError(null)
      setWarning(null)
      setStatus('extracting')
      setProgressLabel('Извлечение текста.')

      await new Promise<void>((resolve) => {
        window.setTimeout(resolve, 400)
      })

      setStatus('generating')
      setProgressLabel('Генерация тест-кейсов...')

      // Большой файл или маркеры `slow`/`notify` → задержка >30с для демо уведомления S3
      const lowerName = file.name.toLowerCase()
      const slowDemo =
        file.size > LONG_DOCUMENT_BYTES ||
        lowerName.includes('slow') ||
        lowerName.includes('notify')
      const delayMs = slowDemo ? 32_000 : 1400
      const outcome = await mockGenerateTestCases(file, settings, { delayMs })

      if (!outcome.ok) {
        setStatus('error')
        setProgressLabel(null)
        setError(outcome.message)
        setResult(null)
        resultRef.current = null
        return
      }

      if (outcome.result.cases.length === 0) {
        setStatus('error')
        setProgressLabel(null)
        setError(ERROR_MESSAGES.API_EMPTY)
        setResult(null)
        resultRef.current = null
        return
      }

      setResult(outcome.result)
      resultRef.current = outcome.result
      setStatus('success')
      setProgressLabel(null)
      maybeNotify(outcome.result)
    },
    [maybeNotify],
  )

  const generate = useCallback(
    async (file: SelectedFileInfo) => {
      if (file.size > LONG_DOCUMENT_BYTES) {
        const ok = window.confirm(ERROR_MESSAGES.LONG_DOCUMENT)
        if (!ok) return
      }
      await runGeneration(file, chunkSettings)
    },
    [chunkSettings, runGeneration],
  )

  const downloadResultCsv = useCallback(() => {
    const current = resultRef.current
    if (!current) return
    const built = downloadCsv(current.cases, current.generatedAt)
    if (built.truncated) {
      setWarning(ERROR_MESSAGES.STEPS_TRUNCATED)
    }
  }, [])

  return {
    status,
    progressLabel,
    error,
    result,
    chunkSettings,
    setChunkSettings,
    showChunkPanel,
    setShowChunkPanel,
    warning,
    clearWarning,
    generate,
    downloadResultCsv,
    clearError,
  }
}

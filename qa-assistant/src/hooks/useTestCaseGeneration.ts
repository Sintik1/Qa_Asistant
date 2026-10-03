import { useCallback, useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import type {
  ChunkSettings,
  GenerationResult,
  GenerationStatus,
  SelectedFileInfo,
  TestCase,
} from '../types'
import {
  chunkSettingsToApi,
  createRun,
  generateRun,
  getHealth,
  getSettings,
  isApiConfigured,
  resolveApiError,
  settingsToChunk,
  uploadDocument,
} from '../api'
import { ERROR_MESSAGES, NOTIFY_AFTER_MS } from '../utils/constants'
import { buildCsvFileName } from '../utils/buildCsvFileName'
import { downloadCsv, type DownloadCsvOptions } from '../utils/csvExport'
import {
  DEFAULT_CHUNK_SETTINGS,
  LONG_DOCUMENT_BYTES,
} from '../utils/chunkSettings'

export interface GenerationContext {
  taskName?: string
  prompt?: string
  requirementsFileName?: string
}

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
  generate: (
    file: SelectedFileInfo,
    context?: GenerationContext,
  ) => Promise<void>
  downloadResultCsv: () => void
  clearError: () => void
  apiReady: boolean | null
}

function csvDownloadOptions(
  result: GenerationResult,
  ctx: GenerationContext,
  fileName?: string,
): DownloadCsvOptions {
  return {
    generatedAt: result.generatedAt,
    taskName: ctx.taskName,
    requirementsFileName: ctx.requirementsFileName,
    ...(fileName ? { fileName } : {}),
  }
}

function mapApiCases(
  items: { name: string; status: string; step: string; expected_result: string }[],
): TestCase[] {
  return items.map((item) => ({
    name: item.name,
    status: 'Approved' as const,
    step: item.step,
    expectedResult: item.expected_result,
  }))
}

/**
 * Реальный поток: document → run → generate → test-cases (Flask + JWT).
 */
export function useTestCaseGeneration(): UseTestCaseGenerationResult {
  const navigate = useNavigate()
  const [status, setStatus] = useState<GenerationStatus>('idle')
  const [progressLabel, setProgressLabel] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [result, setResult] = useState<GenerationResult | null>(null)
  const [chunkSettings, setChunkSettings] = useState<ChunkSettings>(
    DEFAULT_CHUNK_SETTINGS,
  )
  const [showChunkPanel, setShowChunkPanel] = useState(false)
  const [warning, setWarning] = useState<string | null>(null)
  const [apiReady, setApiReady] = useState<boolean | null>(
    isApiConfigured() ? null : false,
  )
  const startedAtRef = useRef<number>(0)
  const resultRef = useRef<GenerationResult | null>(null)
  const exportContextRef = useRef<GenerationContext>({})

  useEffect(() => {
    if (!isApiConfigured()) {
      setApiReady(false)
      return
    }
    let cancelled = false
    void (async () => {
      try {
        const [health, settings] = await Promise.all([getHealth(), getSettings()])
        if (cancelled) return
        setChunkSettings(settingsToChunk(settings))
        setApiReady(Boolean(health.ai?.configured || settings.has_api_token))
      } catch {
        if (!cancelled) setApiReady(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const clearWarning = useCallback(() => setWarning(null), [])
  const clearError = useCallback(() => setError(null), [])

  const failGeneration = useCallback((message: string) => {
    setStatus('error')
    setProgressLabel(null)
    setError(message)
    setResult(null)
    resultRef.current = null
  }, [])

  const maybeNotify = useCallback((next: GenerationResult) => {
    const elapsed = Date.now() - startedAtRef.current
    if (elapsed < NOTIFY_AFTER_MS || !document.hidden) return
    if (!('Notification' in window)) return

    const show = () => {
      const ctx = exportContextRef.current
      const n = new Notification(ERROR_MESSAGES.GENERATION_DONE_NOTIFY)
      n.onclick = () => {
        window.focus()
        downloadCsv(next.cases, csvDownloadOptions(next, ctx))
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
    async (
      file: SelectedFileInfo,
      settings: ChunkSettings,
      context: GenerationContext,
    ) => {
      if (!isApiConfigured()) {
        failGeneration(
          'Не задан VITE_API_BASE_URL. Укажите URL Flask API в qa-assistant/.env.local',
        )
        return
      }

      startedAtRef.current = Date.now()
      exportContextRef.current = {
        taskName: context.taskName,
        prompt: context.prompt,
        requirementsFileName: context.requirementsFileName ?? file.name,
      }
      setError(null)
      setWarning(null)
      setStatus('extracting')
      setProgressLabel('Извлечение текста.')

      try {
        const uploaded = await uploadDocument(file.file)
        const requirementsText = uploaded.text.trim()
        if (!requirementsText) {
          failGeneration(ERROR_MESSAGES.EMPTY_FILE)
          return
        }

        setStatus('generating')
        setProgressLabel('Генерация тест-кейсов...')

        const run = await createRun({
          document_id: uploaded.document.id,
          ...chunkSettingsToApi(settings),
        })

        const generated = await generateRun(run.id, {
          requirements_text: requirementsText,
          task_name: context.taskName,
          prompt: context.prompt,
        })

        const cases = mapApiCases(generated.items)
        if (cases.length === 0) {
          failGeneration(ERROR_MESSAGES.API_EMPTY)
          return
        }

        const next: GenerationResult = {
          cases,
          truncated: false,
          generatedAt: new Date(),
        }
        setResult(next)
        resultRef.current = next
        setStatus('success')
        setProgressLabel(null)
        maybeNotify(next)
      } catch (err) {
        const resolved = resolveApiError(err)
        if (resolved.requestId) {
          console.warn('[api]', resolved.message, 'request_id=', resolved.requestId)
        }
        failGeneration(resolved.message)
        if (resolved.redirectTo) {
          navigate(resolved.redirectTo)
        }
      }
    },
    [failGeneration, maybeNotify, navigate],
  )

  const generate = useCallback(
    async (file: SelectedFileInfo, context: GenerationContext = {}) => {
      if (file.size > LONG_DOCUMENT_BYTES) {
        const ok = window.confirm(ERROR_MESSAGES.LONG_DOCUMENT)
        if (!ok) return
      }
      await runGeneration(file, chunkSettings, context)
    },
    [chunkSettings, runGeneration],
  )

  const downloadResultCsv = useCallback(() => {
    const current = resultRef.current
    if (!current) return
    const ctx = exportContextRef.current
    const built = downloadCsv(
      current.cases,
      csvDownloadOptions(
        current,
        ctx,
        buildCsvFileName(ctx.taskName ?? '', ctx.requirementsFileName),
      ),
    )
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
    apiReady,
  }
}

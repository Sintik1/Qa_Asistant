import { useCallback, useRef, useState } from 'react'
import type {
  ChunkSettings,
  GenerationResult,
  GenerationStatus,
  SelectedFileInfo,
} from '../types'
import { ERROR_MESSAGES, NOTIFY_AFTER_MS } from '../utils/constants'
import { buildCsvFileName } from '../utils/buildCsvFileName'
import { downloadCsv, type DownloadCsvOptions } from '../utils/csvExport'
import {
  DEFAULT_CHUNK_SETTINGS,
  isSlowDemoFile,
  LONG_DOCUMENT_BYTES,
  mockGenerateTestCases,
} from '../utils/mockGeneration'

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

function delay(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
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
  const exportContextRef = useRef<GenerationContext>({})

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

      await delay(400)

      setStatus('generating')
      setProgressLabel('Генерация тест-кейсов...')

      // Большой файл или маркеры `slow`/`notify` → задержка >30с для демо уведомления S3
      const delayMs = isSlowDemoFile(file) ? 32_000 : 1400
      const outcome = await mockGenerateTestCases(file, settings, {
        delayMs,
        taskName: context.taskName,
        prompt: context.prompt,
      })

      if (!outcome.ok) {
        failGeneration(outcome.message)
        return
      }

      if (outcome.result.cases.length === 0) {
        failGeneration(ERROR_MESSAGES.API_EMPTY)
        return
      }

      setResult(outcome.result)
      resultRef.current = outcome.result
      setStatus('success')
      setProgressLabel(null)
      maybeNotify(outcome.result)
    },
    [failGeneration, maybeNotify],
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
  }
}

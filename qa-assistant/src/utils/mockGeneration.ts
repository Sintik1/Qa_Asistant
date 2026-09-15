import { MOCK_TEST_CASES } from '../mocks/mockTestCases'
import type { ChunkSettings, GenerationResult, SelectedFileInfo } from '../types'
import { ERROR_MESSAGES } from './constants'

/** Файлы больше порога показывают confirm «длинный документ» (эвристика mock). */
export const LONG_DOCUMENT_BYTES = 5 * 1024 * 1024

export const DEFAULT_CHUNK_SETTINGS: ChunkSettings = {
  chunkSize: 4000,
  chunkOverlap: 200,
  chunkMethod: 'header',
}

/**
 * Подстроки в имени файла для негативных/демо сценариев.
 * Правила `includes` должны оставаться бит-идентичными.
 */
export const MOCK_FILENAME_MARKERS = {
  noRequirements: ['empty', 'noreq'],
  corrupt: ['corrupt', 'broken'],
  apiFail: ['fail', 'apierror'],
  slowDemo: ['slow', 'notify'],
} as const

export type MockGenerationOutcome =
  | { ok: true; result: GenerationResult }
  | { ok: false; message: string }

export interface MockGenerationOptions {
  delayMs?: number
  taskName?: string
  prompt?: string
}

function filenameIncludesAny(
  fileName: string,
  markers: readonly string[],
): boolean {
  const lower = fileName.toLowerCase()
  return markers.some((marker) => lower.includes(marker))
}

/** Большой файл или маркеры `slow`/`notify` — демо уведомления S3. */
export function isSlowDemoFile(file: SelectedFileInfo): boolean {
  return (
    file.size > LONG_DOCUMENT_BYTES ||
    filenameIncludesAny(file.name, MOCK_FILENAME_MARKERS.slowDemo)
  )
}

/**
 * Mock пайплайна на фронте: извлечение → чанкинг → генерация ИИ.
 * Маркеры в имени файла для негативных сценариев (ручная проверка):
 * - `empty` / `noreq` → нет требований
 * - `corrupt` / `broken` → повреждённый файл
 * - `fail` / `apierror` → API недоступен
 * - `slow` / `notify` → долгая генерация (уведомление S3)
 */
export async function mockGenerateTestCases(
  file: SelectedFileInfo,
  settings: ChunkSettings,
  options?: MockGenerationOptions,
): Promise<MockGenerationOutcome> {
  const delayMs = options?.delayMs ?? 1200
  await wait(delayMs)

  if (filenameIncludesAny(file.name, MOCK_FILENAME_MARKERS.noRequirements)) {
    return { ok: false, message: ERROR_MESSAGES.NO_REQUIREMENTS }
  }

  if (filenameIncludesAny(file.name, MOCK_FILENAME_MARKERS.corrupt)) {
    return { ok: false, message: ERROR_MESSAGES.CORRUPT_FILE }
  }

  if (filenameIncludesAny(file.name, MOCK_FILENAME_MARKERS.apiFail)) {
    return { ok: false, message: ERROR_MESSAGES.API_UNAVAILABLE }
  }

  const taskLabel = options?.taskName?.trim()
  const promptNote = options?.prompt?.trim()

  // Небольшая вариация по настройкам чанков, чтобы перегенерация отличалась
  const take = Math.min(
    MOCK_TEST_CASES.length,
    Math.max(2, Math.round(settings.chunkSize / 1500)),
  )
  const overlapShift = settings.chunkOverlap % MOCK_TEST_CASES.length
  const rotated = [
    ...MOCK_TEST_CASES.slice(overlapShift),
    ...MOCK_TEST_CASES.slice(0, overlapShift),
  ]

  return {
    ok: true,
    result: {
      cases: rotated.slice(0, take).map((c) => {
        const namePrefix = taskLabel
          ? `[${settings.chunkMethod}][${taskLabel}] `
          : `[${settings.chunkMethod}] `
        const stepSuffix = promptNote
          ? `\n\n[Промт] ${promptNote}`
          : ''
        return {
          ...c,
          name: `${namePrefix}${c.name}`,
          step: `${c.step}${stepSuffix}`,
        }
      }),
      truncated: false,
      generatedAt: new Date(),
    },
  }
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    setTimeout(resolve, ms)
  })
}

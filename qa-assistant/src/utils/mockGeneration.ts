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

export type MockGenerationOutcome =
  | { ok: true; result: GenerationResult }
  | { ok: false; message: string }

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
  options?: { delayMs?: number },
): Promise<MockGenerationOutcome> {
  const delayMs = options?.delayMs ?? 1200
  await wait(delayMs)

  const lower = file.name.toLowerCase()

  if (lower.includes('empty') || lower.includes('noreq')) {
    return { ok: false, message: ERROR_MESSAGES.NO_REQUIREMENTS }
  }

  if (lower.includes('corrupt') || lower.includes('broken')) {
    return { ok: false, message: ERROR_MESSAGES.CORRUPT_FILE }
  }

  if (lower.includes('fail') || lower.includes('apierror')) {
    return { ok: false, message: ERROR_MESSAGES.API_UNAVAILABLE }
  }

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
      cases: rotated.slice(0, take).map((c) => ({
        ...c,
        name: `[${settings.chunkMethod}] ${c.name}`,
      })),
      truncated: false,
      generatedAt: new Date(),
    },
  }
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms)
  })
}

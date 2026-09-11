import { afterEach, describe, expect, it, vi } from 'vitest'
import { ERROR_MESSAGES } from './constants'
import {
  DEFAULT_CHUNK_SETTINGS,
  mockGenerateTestCases,
} from './mockGeneration'
import type { SelectedFileInfo } from '../types'

function fileInfo(name: string, size = 1024): SelectedFileInfo {
  const file = new File(['requirements'], name, { type: 'text/plain' })
  return { name, size, file }
}

describe('mockGenerateTestCases', () => {
  afterEach(() => {
    vi.useRealTimers()
  })

  it('returns success cases with chunk method prefix', async () => {
    const outcome = await mockGenerateTestCases(
      fileInfo('fd.pdf'),
      { ...DEFAULT_CHUNK_SETTINGS, chunkMethod: 'fixed', chunkSize: 4000 },
      { delayMs: 0 },
    )
    expect(outcome.ok).toBe(true)
    if (!outcome.ok) return
    expect(outcome.result.cases.length).toBeGreaterThan(0)
    expect(outcome.result.cases[0]?.name.startsWith('[fixed] ')).toBe(true)
  })

  it.each([
    ['empty_reqs.md', ERROR_MESSAGES.NO_REQUIREMENTS],
    ['noreq.pdf', ERROR_MESSAGES.NO_REQUIREMENTS],
    ['corrupt.docx', ERROR_MESSAGES.CORRUPT_FILE],
    ['broken.doc', ERROR_MESSAGES.CORRUPT_FILE],
    ['fail.pdf', ERROR_MESSAGES.API_UNAVAILABLE],
    ['apierror.md', ERROR_MESSAGES.API_UNAVAILABLE],
  ])('negative marker %s → %s', async (name, message) => {
    const outcome = await mockGenerateTestCases(
      fileInfo(name),
      DEFAULT_CHUNK_SETTINGS,
      { delayMs: 0 },
    )
    expect(outcome).toEqual({ ok: false, message })
  })

  it('respects delayMs (non-flaky fake timers)', async () => {
    vi.useFakeTimers()
    const promise = mockGenerateTestCases(
      fileInfo('ok.pdf'),
      DEFAULT_CHUNK_SETTINGS,
      { delayMs: 500 },
    )
    await vi.advanceTimersByTimeAsync(500)
    const outcome = await promise
    expect(outcome.ok).toBe(true)
  })
})

import { describe, expect, it } from 'vitest'
import { buildTimestampedFileName } from './buildTimestampedFileName'

describe('buildTimestampedFileName', () => {
  it('formats csv name by TZ pattern', () => {
    const date = new Date(2026, 8, 11, 14, 5, 9)
    expect(buildTimestampedFileName('csv', date)).toBe(
      'test_cases_20260911_140509.csv',
    )
  })

  it('formats docx name by TZ pattern', () => {
    const date = new Date(2026, 0, 2, 3, 4, 5)
    expect(buildTimestampedFileName('docx', date)).toBe(
      'test_cases_20260102_030405.docx',
    )
  })
})

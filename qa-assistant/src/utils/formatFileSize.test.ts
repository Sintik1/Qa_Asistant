import { describe, expect, it } from 'vitest'
import { formatFileSize } from './formatFileSize'

describe('formatFileSize', () => {
  it.each([
    [0, '0 Б'],
    [512, '512 Б'],
    [1024, '1.0 КБ'],
    [1536, '1.5 КБ'],
    [1024 * 1024, '1.0 МБ'],
    [2.5 * 1024 * 1024, '2.5 МБ'],
  ])('%s bytes → %s', (bytes, expected) => {
    expect(formatFileSize(bytes)).toBe(expected)
  })
})

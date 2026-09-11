import { describe, expect, it } from 'vitest'
import { buildCsvFileName } from './buildCsvFileName'

describe('buildCsvFileName', () => {
  it('uses task name when provided', () => {
    expect(buildCsvFileName('CRM-1234 Map')).toBe(
      'Тест кейсы_CRM-1234 Map.csv',
    )
  })

  it('falls back to requirements file stem', () => {
    expect(buildCsvFileName('  ', 'requirements.docx')).toBe(
      'Тест кейсы_requirements.csv',
    )
  })

  it('falls back to result when both empty', () => {
    expect(buildCsvFileName('')).toBe('Тест кейсы_result.csv')
  })

  it.each([
    ['a/b:c*?"<>|', 'Тест кейсы_a_b_c_.csv'],
    ['ok-name', 'Тест кейсы_ok-name.csv'],
  ])('sanitizes unsafe chars in %s', (raw, expected) => {
    expect(buildCsvFileName(raw)).toBe(expected)
  })
})

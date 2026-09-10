import type { TestCase } from '../types'
import { buildTimestampedFileName } from './buildTimestampedFileName'

const CSV_HEADERS = ['Name', 'Status', 'Step', 'Expected Result'] as const
const EXCEL_CELL_LIMIT = 32767

function escapeCsvCell(value: string): string {
  const needsQuotes = /[",\r\n]/.test(value)
  const escaped = value.replace(/"/g, '""')
  return needsQuotes ? `"${escaped}"` : escaped
}

export interface CsvBuildResult {
  content: string
  truncated: boolean
}

/** Собирает CSV в UTF-8 с BOM для TestRail/Zephyr. */
export function buildCsvContent(cases: TestCase[]): CsvBuildResult {
  let truncated = false
  const lines = [CSV_HEADERS.join(',')]

  for (const item of cases) {
    let step = item.step
    let expected = item.expectedResult
    if (step.length > EXCEL_CELL_LIMIT) {
      step = step.slice(0, EXCEL_CELL_LIMIT)
      truncated = true
    }
    if (expected.length > EXCEL_CELL_LIMIT) {
      expected = expected.slice(0, EXCEL_CELL_LIMIT)
      truncated = true
    }
    lines.push(
      [
        escapeCsvCell(item.name),
        escapeCsvCell(item.status),
        escapeCsvCell(step),
        escapeCsvCell(expected),
      ].join(','),
    )
  }

  // UTF-8 BOM для Excel (ТЗ §3.3 / M3)
  const content = `\uFEFF${lines.join('\r\n')}`
  return { content, truncated }
}

export function downloadCsv(cases: TestCase[], generatedAt?: Date): CsvBuildResult {
  const result = buildCsvContent(cases)
  const blob = new Blob([result.content], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = buildTimestampedFileName('csv', generatedAt ?? new Date())
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  return result
}

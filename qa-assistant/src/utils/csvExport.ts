import type { TestCase } from '../types'
import { buildCsvFileName } from './buildCsvFileName'
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
  fileName: string
}

export interface DownloadCsvOptions {
  generatedAt?: Date
  /** Имя задачи из формы (приоритет для имени файла по UI/Figma). */
  taskName?: string
  /** Имя файла требований — fallback, если taskName пуст. */
  requirementsFileName?: string
  /**
   * Явное имя файла. Если не задано — `Тест кейсы_<название>.csv`
   * (buildCsvFileName). Timestamp-имя оставляем только как legacy opt-in.
   */
  fileName?: string
  useTimestampName?: boolean
}

/** Собирает CSV в UTF-8 с BOM для TestRail/Zephyr. */
export function buildCsvContent(cases: TestCase[]): Omit<CsvBuildResult, 'fileName'> {
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

export function resolveDownloadCsvFileName(opts: DownloadCsvOptions): string {
  if (opts.fileName) return opts.fileName
  if (opts.useTimestampName) {
    return buildTimestampedFileName('csv', opts.generatedAt ?? new Date())
  }
  return buildCsvFileName(opts.taskName ?? '', opts.requirementsFileName)
}

export function downloadCsv(
  cases: TestCase[],
  options: DownloadCsvOptions | Date = {},
): CsvBuildResult {
  // Обратная совместимость: раньше вторым аргументом был Date
  const opts: DownloadCsvOptions =
    options instanceof Date ? { generatedAt: options } : options

  const built = buildCsvContent(cases)
  const fileName = resolveDownloadCsvFileName(opts)

  const blob = new Blob([built.content], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = fileName
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
  return { ...built, fileName }
}

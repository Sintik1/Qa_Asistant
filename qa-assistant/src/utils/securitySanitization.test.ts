import { describe, expect, it } from 'vitest'
import { buildCsvFileName } from './buildCsvFileName'
import { buildCsvContent } from './csvExport'

/**
 * Security-oriented unit checks for frontend data handling.
 * XSS/SQLi payloads must remain data (escaped / sanitized), never executable.
 */
const XSS_PAYLOADS = [
  '<script>alert(1)</script>',
  '"><img src=x onerror=alert(1)>',
  '<svg onload=alert(1)>',
]

const SQLI_PAYLOADS = [
  "' OR '1'='1",
  '1; DROP TABLE users;--',
  "admin'--",
]

describe('security: filename / CSV treat payloads as data', () => {
  it.each(XSS_PAYLOADS)('CSV stores XSS payload as plain data %s', (payload) => {
    const { content } = buildCsvContent([
      {
        name: payload,
        status: 'Approved',
        step: 'step',
        expectedResult: 'ok',
      },
    ])
    // Payload is serialized as CSV text (quotes escaped), not executed.
    expect(content).toContain(payload.replace(/"/g, '""'))
    expect(content.startsWith('\uFEFF')).toBe(true)
  })

  it.each(SQLI_PAYLOADS)('filename sanitizes path-like SQLi %s', (payload) => {
    const name = buildCsvFileName(payload)
    expect(name.endsWith('.csv')).toBe(true)
    expect(name).not.toMatch(/[\\/:*?"<>|]/)
  })

  it.each(XSS_PAYLOADS)('filename sanitizes XSS for download name %s', (payload) => {
    const name = buildCsvFileName(payload)
    expect(name).toContain('Тест кейсы_')
    expect(name).not.toMatch(/[<>:"/\\|?*]/)
  })
})

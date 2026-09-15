import { describe, expect, it } from 'vitest'
import type { TestCase } from '../types'
import { buildCsvContent, resolveDownloadCsvFileName } from './csvExport'

const sample: TestCase[] = [
  {
    name: 'Case "A"',
    status: 'Approved',
    step: '1. Open\n2. Click',
    expectedResult: 'OK, done',
  },
]

describe('buildCsvContent', () => {
  it('adds UTF-8 BOM and CRLF rows with headers', () => {
    const { content, truncated } = buildCsvContent(sample)
    expect(truncated).toBe(false)
    expect(content.startsWith('\uFEFF')).toBe(true)
    expect(content).toContain('Name,Status,Step,Expected Result')
    expect(content).toContain('\r\n')
    expect(content).toContain('"Case ""A"""')
    expect(content).toContain('"1. Open\n2. Click"')
    expect(content).toContain('"OK, done"')
  })

  it('marks truncated when cell exceeds Excel limit', () => {
    const long = 'x'.repeat(32768)
    const { truncated, content } = buildCsvContent([
      {
        name: 'Long',
        status: 'Approved',
        step: long,
        expectedResult: 'ok',
      },
    ])
    expect(truncated).toBe(true)
    expect(content.includes(long)).toBe(false)
    expect(content).toContain('x'.repeat(32767))
  })
})

describe('resolveDownloadCsvFileName', () => {
  it('uses UI pattern Тест кейсы_<task>.csv by default', () => {
    expect(
      resolveDownloadCsvFileName({ taskName: 'CRM-AI-DEBUG' }),
    ).toBe('Тест кейсы_CRM-AI-DEBUG.csv')
  })

  it('falls back to requirements file stem', () => {
    expect(
      resolveDownloadCsvFileName({
        taskName: '',
        requirementsFileName: 'requirements.md',
      }),
    ).toBe('Тест кейсы_requirements.csv')
  })
})

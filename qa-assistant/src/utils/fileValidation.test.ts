import { describe, expect, it } from 'vitest'
import { ERROR_MESSAGES, MAX_FILE_SIZE_BYTES } from './constants'
import {
  getFileExtension,
  isAllowedExtension,
  validateUploadFile,
} from './fileValidation'

function makeFile(
  name: string,
  sizeBytes: number,
  content = 'x',
): File {
  const blobParts = [content.repeat(Math.max(1, Math.min(sizeBytes, 64)))]
  const file = new File(blobParts, name, { type: 'application/octet-stream' })
  Object.defineProperty(file, 'size', { value: sizeBytes })
  return file
}

describe('getFileExtension', () => {
  it.each([
    ['spec.pdf', '.pdf'],
    ['REQ.DOCX', '.docx'],
    ['a.b.md', '.md'],
    ['noext', ''],
    ['.hidden', '.hidden'],
  ])('parses %s → %s', (name, expected) => {
    expect(getFileExtension(name)).toBe(expected)
  })
})

describe('isAllowedExtension', () => {
  it.each(['.pdf', '.docx', '.doc', '.md'] as const)(
    'allows %s',
    (ext) => {
      expect(isAllowedExtension(ext)).toBe(true)
    },
  )

  it.each(['.txt', '.exe', '.PDF', ''])('rejects %s', (ext) => {
    expect(isAllowedExtension(ext)).toBe(false)
  })
})

describe('validateUploadFile — positive', () => {
  it.each(['req.pdf', 'a.docx', 'b.doc', 'notes.md'])(
    'accepts valid file %s',
    (name) => {
      expect(validateUploadFile(makeFile(name, 128))).toEqual({ ok: true })
    },
  )
})

describe('validateUploadFile — negative', () => {
  it('rejects unsupported format with TZ message', () => {
    expect(validateUploadFile(makeFile('virus.exe', 10))).toEqual({
      ok: false,
      errorCode: 'INVALID_FORMAT',
      message: ERROR_MESSAGES.INVALID_FORMAT,
    })
  })

  it('rejects empty file', () => {
    expect(validateUploadFile(makeFile('empty.md', 0))).toEqual({
      ok: false,
      errorCode: 'EMPTY_FILE',
      message: ERROR_MESSAGES.EMPTY_FILE,
    })
  })

  it('rejects oversized file', () => {
    expect(
      validateUploadFile(makeFile('huge.pdf', MAX_FILE_SIZE_BYTES + 1)),
    ).toEqual({
      ok: false,
      errorCode: 'FILE_TOO_LARGE',
      message: ERROR_MESSAGES.FILE_TOO_LARGE,
    })
  })

  it('accepts file exactly at size limit', () => {
    expect(
      validateUploadFile(makeFile('edge.pdf', MAX_FILE_SIZE_BYTES)),
    ).toEqual({ ok: true })
  })
})

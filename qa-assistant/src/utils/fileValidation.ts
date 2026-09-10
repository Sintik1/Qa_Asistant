import {
  ALLOWED_EXTENSIONS,
  ERROR_MESSAGES,
  MAX_FILE_SIZE_BYTES,
} from './constants'
import type { AllowedFileExtension, FileValidationResult } from '../types'

export function getFileExtension(fileName: string): string {
  const idx = fileName.lastIndexOf('.')
  if (idx < 0) return ''
  return fileName.slice(idx).toLowerCase()
}

export function isAllowedExtension(
  extension: string,
): extension is AllowedFileExtension {
  return (ALLOWED_EXTENSIONS as readonly string[]).includes(extension)
}

/** Validates file format and size per TZ acceptance criteria. */
export function validateUploadFile(file: File): FileValidationResult {
  const extension = getFileExtension(file.name)

  if (!isAllowedExtension(extension)) {
    return {
      ok: false,
      errorCode: 'INVALID_FORMAT',
      message: ERROR_MESSAGES.INVALID_FORMAT,
    }
  }

  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      ok: false,
      errorCode: 'FILE_TOO_LARGE',
      message: ERROR_MESSAGES.FILE_TOO_LARGE,
    }
  }

  if (file.size === 0) {
    return {
      ok: false,
      errorCode: 'EMPTY_FILE',
      message: ERROR_MESSAGES.EMPTY_FILE,
    }
  }

  return { ok: true }
}

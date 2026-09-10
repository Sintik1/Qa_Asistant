import { useCallback, useState } from 'react'
import { validateUploadFile } from '../utils/fileValidation'
import type { SelectedFileInfo } from '../types'

interface UseFileUploadResult {
  file: SelectedFileInfo | null
  error: string | null
  setFromFile: (next: File | null) => void
  clear: () => void
}

/** Локальное состояние загрузки + валидация по ТЗ (формат / размер). */
export function useFileUpload(): UseFileUploadResult {
  const [file, setFile] = useState<SelectedFileInfo | null>(null)
  const [error, setError] = useState<string | null>(null)

  const setFromFile = useCallback((next: File | null) => {
    if (!next) {
      setFile(null)
      setError(null)
      return
    }

    const result = validateUploadFile(next)
    if (!result.ok) {
      setFile(null)
      setError(result.message ?? 'Ошибка файла')
      return
    }

    setFile({ name: next.name, size: next.size, file: next })
    setError(null)
  }, [])

  const clear = useCallback(() => {
    setFile(null)
    setError(null)
  }, [])

  return { file, error, setFromFile, clear }
}

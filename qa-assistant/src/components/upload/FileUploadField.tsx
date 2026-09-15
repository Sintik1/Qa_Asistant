import { useEffect, useRef } from 'react'
import { ACCEPT_FILE_TYPES } from '../../utils/constants'
import { formatFileSize } from '../../utils/formatFileSize'
import type { SelectedFileInfo } from '../../types'

interface FileUploadFieldProps {
  id: string
  label: string
  selectedFile: SelectedFileInfo | null
  onFileChange: (file: File | null) => void
  error?: string
}

export function FileUploadField({
  id,
  label,
  selectedFile,
  onFileChange,
  error,
}: FileUploadFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null)

  // B2: после reject/clear сбрасываем native value, иначе UI показывает старое имя файла.
  useEffect(() => {
    if (!selectedFile && inputRef.current) {
      inputRef.current.value = ''
    }
  }, [selectedFile, error])

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-sm font-medium text-slate-800">
        {label}
      </label>
      <input
        ref={inputRef}
        id={id}
        type="file"
        accept={ACCEPT_FILE_TYPES}
        className="block w-full max-w-full text-sm text-slate-700 file:mr-0 file:mb-2 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-800 hover:file:bg-slate-200 sm:file:mb-0 sm:file:mr-3"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null
          onFileChange(file)
        }}
      />
      {/* B1: не дублируем «Файл не выбран» — native input уже показывает статус */}
      {selectedFile ? (
        <p className="text-sm text-slate-500">
          {selectedFile.name} ({formatFileSize(selectedFile.size)})
        </p>
      ) : null}
      {error ? (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  )
}

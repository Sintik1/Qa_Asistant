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
  return (
    <div className="space-y-2">
      <label htmlFor={id} className="block text-sm font-medium text-slate-800">
        {label}
      </label>
      <input
        id={id}
        type="file"
        accept={ACCEPT_FILE_TYPES}
        className="block w-full text-sm text-slate-700 file:mr-3 file:rounded-md file:border-0 file:bg-slate-100 file:px-3 file:py-2 file:text-sm file:font-medium file:text-slate-800 hover:file:bg-slate-200"
        onChange={(event) => {
          const file = event.target.files?.[0] ?? null
          onFileChange(file)
        }}
      />
      <p className="text-sm text-slate-500">
        {selectedFile
          ? `${selectedFile.name} (${formatFileSize(selectedFile.size)})`
          : 'Файл не выбран'}
      </p>
      {error ? (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  )
}

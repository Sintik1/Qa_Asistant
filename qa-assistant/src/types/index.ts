/** Shared domain types for QA Assistant UI (aligned with TZ + Figma). */

export type AllowedFileExtension = '.pdf' | '.docx' | '.doc' | '.md'

export type FileValidationErrorCode =
  | 'INVALID_FORMAT'
  | 'FILE_TOO_LARGE'
  | 'EMPTY_FILE'

export interface FileValidationResult {
  ok: boolean
  errorCode?: FileValidationErrorCode
  message?: string
}

export interface SelectedFileInfo {
  name: string
  size: number
  file: File
}

export interface GenerationFormState {
  requirementsFile: SelectedFileInfo | null
  templatesFile: SelectedFileInfo | null
  taskName: string
  prompt: string
  projectId: string
}

export type GenerationStatus =
  | 'idle'
  | 'extracting'
  | 'generating'
  | 'success'
  | 'error'

export interface AppErrorState {
  message: string
  actionLabel?: string
}

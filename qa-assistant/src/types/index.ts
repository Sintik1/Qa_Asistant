/** Общие доменные типы UI QA Assistant (по ТЗ + Figma). */

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

/** Строка CSV: колонки TestRail/Zephyr (ТЗ §6.1). */
export interface TestCase {
  name: string
  status: 'Approved'
  step: string
  expectedResult: string
}

export type ChunkMethod = 'header' | 'fixed' | 'recursive'

export interface ChunkSettings {
  chunkSize: number
  chunkOverlap: number
  chunkMethod: ChunkMethod
}

export interface GenerationResult {
  cases: TestCase[]
  truncated: boolean
  generatedAt: Date
}

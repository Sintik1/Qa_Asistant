import type { ChunkSettings } from '../types'

export const DEFAULT_CHUNK_SETTINGS: ChunkSettings = {
  chunkSize: 4000,
  chunkOverlap: 200,
  chunkMethod: 'header',
}

/** Файлы больше порога показывают confirm «длинный документ». */
export const LONG_DOCUMENT_BYTES = 5 * 1024 * 1024

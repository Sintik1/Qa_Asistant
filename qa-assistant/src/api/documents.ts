import { apiFetch } from '../lib/apiClient'
import { apiJson } from './client'
import { parseApiError } from './errors'
import type { ApiDocument } from './types'

export interface UploadDocumentResult {
  document: ApiDocument
  text: string
  char_count: number
}

export async function createDocument(input: {
  original_filename: string
  size_bytes: number
  mime_type?: string | null
}): Promise<ApiDocument> {
  return apiJson<ApiDocument>('/api/documents', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

/** Multipart upload → server extract + Storage/local persist. */
export async function uploadDocument(file: File): Promise<UploadDocumentResult> {
  const form = new FormData()
  form.append('file', file, file.name)
  const response = await apiFetch('/api/documents/upload', {
    method: 'POST',
    body: form,
  })
  if (!response.ok) {
    throw await parseApiError(response)
  }
  return (await response.json()) as UploadDocumentResult
}

export async function listDocuments(): Promise<ApiDocument[]> {
  const body = await apiJson<{ items: ApiDocument[] }>('/api/documents')
  return body.items
}

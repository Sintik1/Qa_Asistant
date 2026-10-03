import { apiJson } from './client'
import type { ApiDocument } from './types'

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

export async function listDocuments(): Promise<ApiDocument[]> {
  const body = await apiJson<{ items: ApiDocument[] }>('/api/documents')
  return body.items
}

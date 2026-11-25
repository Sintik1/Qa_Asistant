import { apiJson } from './client'

export type ChatCitation = {
  document_id: string
  section_number?: string | null
  section_path?: string | null
  title?: string | null
  similarity?: number | null
  preview?: string
  source_kind?: 'requirement' | 'case' | string
  url?: string | null
}

export type ChatResponse = {
  answer: string
  citations: ChatCitation[]
}

export async function chatRequirements(input: {
  question: string
  document_id?: string
  include_cases?: boolean
}): Promise<ChatResponse> {
  const payload: Record<string, unknown> = { question: input.question }
  if (input.document_id) payload.document_id = input.document_id
  if (typeof input.include_cases === 'boolean') {
    payload.include_cases = input.include_cases
  }
  return apiJson<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export type ConfluenceSyncResult = {
  space: string
  pages: number
  indexed: number
  skipped: number
}

export function syncConfluenceSpace(): Promise<ConfluenceSyncResult> {
  return apiJson<ConfluenceSyncResult>('/api/rag/confluence/sync', { method: 'POST' })
}

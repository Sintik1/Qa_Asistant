import { apiJson } from './client'

export type ChatCitation = {
  document_id: string
  section_number?: string | null
  section_path?: string | null
  title?: string | null
  similarity?: number | null
  preview?: string
}

export type ChatResponse = {
  answer: string
  citations: ChatCitation[]
}

export async function chatRequirements(input: {
  question: string
  document_id?: string
}): Promise<ChatResponse> {
  return apiJson<ChatResponse>('/api/chat', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

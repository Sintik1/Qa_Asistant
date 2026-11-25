import { apiFetch } from '../lib/apiClient'
import { apiJson } from './client'
import { parseApiError } from './errors'

export interface LibraryItem {
  id: string
  name: string
  content: string
  created_at?: string | null
  updated_at?: string | null
}

export type LibraryKind = 'prompt' | 'template'

const PATH: Record<LibraryKind, string> = {
  prompt: '/api/prompts',
  template: '/api/scenario-templates',
}

export async function listLibrary(kind: LibraryKind): Promise<LibraryItem[]> {
  const body = await apiJson<{ items: LibraryItem[] }>(PATH[kind])
  return body.items
}

export async function createLibraryItem(
  kind: LibraryKind,
  input: { name: string; content: string },
): Promise<LibraryItem> {
  return apiJson<LibraryItem>(PATH[kind], {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function deleteLibraryItem(kind: LibraryKind, id: string): Promise<void> {
  await apiJson<void>(`${PATH[kind]}/${id}`, { method: 'DELETE' })
}

export async function extractLibraryFile(file: File): Promise<{ text: string; char_count: number }> {
  const form = new FormData()
  form.append('file', file, file.name)
  const response = await apiFetch('/api/library/extract-text', {
    method: 'POST',
    body: form,
  })
  if (!response.ok) {
    throw await parseApiError(response)
  }
  return (await response.json()) as { text: string; char_count: number }
}

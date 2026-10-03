import { apiFetch } from '../lib/apiClient'
import { parseApiError } from './errors'

export function isApiConfigured(): boolean {
  const base = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim()
  return Boolean(base)
}

export async function apiJson<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const response = await apiFetch(path, init)
  if (!response.ok) {
    throw await parseApiError(response)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

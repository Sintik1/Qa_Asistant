import { apiFetch } from '../lib/apiClient'
import { parseApiError } from './errors'

export function apiBaseUrl(): string {
  return ((import.meta.env.VITE_API_BASE_URL as string | undefined) ?? '').trim().replace(/\/$/, '')
}

export function isApiConfigured(): boolean {
  return Boolean(apiBaseUrl())
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

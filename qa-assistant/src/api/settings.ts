import { apiJson } from './client'
import type { ApiHealth, ApiUserSettings } from './types'
import type { ChunkSettings } from '../types'

export async function getSettings(): Promise<ApiUserSettings> {
  return apiJson<ApiUserSettings>('/api/settings')
}

export async function patchSettings(
  patch: Partial<{
    chunk_size: number
    chunk_overlap: number
    chunk_method: string
    has_api_token: boolean
  }>,
): Promise<ApiUserSettings> {
  return apiJson<ApiUserSettings>('/api/settings', {
    method: 'PATCH',
    body: JSON.stringify(patch),
  })
}

export async function getHealth(): Promise<ApiHealth> {
  return apiJson<ApiHealth>('/api/health')
}

export function settingsToChunk(settings: ApiUserSettings): ChunkSettings {
  return {
    chunkSize: settings.chunk_size,
    chunkOverlap: settings.chunk_overlap,
    chunkMethod: settings.chunk_method,
  }
}

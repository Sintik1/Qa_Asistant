import { apiJson } from './client'
import type { ApiRun, ApiTestCase, GenerateResponse } from './types'
import type { ChunkSettings } from '../types'

export async function createRun(input: {
  document_id: string
  chunk_size?: number
  chunk_overlap?: number
  chunk_method?: string
}): Promise<ApiRun> {
  return apiJson<ApiRun>('/api/runs', {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export async function listRuns(): Promise<ApiRun[]> {
  const body = await apiJson<{ items: ApiRun[] }>('/api/runs')
  return body.items
}

export async function listTestCases(runId: string): Promise<ApiTestCase[]> {
  const body = await apiJson<{ items: ApiTestCase[] }>(
    `/api/runs/${runId}/test-cases`,
  )
  return body.items
}

export async function generateRun(
  runId: string,
  input: {
    requirements_text: string
    task_name?: string
    prompt?: string
  },
): Promise<GenerateResponse> {
  return apiJson<GenerateResponse>(`/api/runs/${runId}/generate`, {
    method: 'POST',
    body: JSON.stringify(input),
  })
}

export function chunkSettingsToApi(settings: ChunkSettings) {
  return {
    chunk_size: settings.chunkSize,
    chunk_overlap: settings.chunkOverlap,
    chunk_method: settings.chunkMethod,
  }
}

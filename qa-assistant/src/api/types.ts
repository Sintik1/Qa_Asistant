/** DTOs from Flask hybrid API (snake_case as returned by backend). */

export interface ApiDocument {
  id: string
  user_id: string
  original_filename: string
  mime_type: string | null
  size_bytes: number
  storage_path: string
  status: string
  created_at: string | null
}

export interface ApiRun {
  id: string
  user_id: string
  document_id: string
  status: string
  chunk_size: number
  chunk_overlap: number
  chunk_method: string
  error_message: string | null
  case_count: number
  created_at: string | null
}

export interface ApiTestCase {
  id: string
  run_id: string
  user_id: string
  name: string
  status: string
  step: string
  expected_result: string
  sort_order: number
  chunk_id: string | null
}

export interface ApiUserSettings {
  user_id: string
  chunk_size: number
  chunk_overlap: number
  chunk_method: 'header' | 'fixed' | 'recursive'
  has_api_token: boolean
}

export interface ApiHealth {
  status: string
  api: string
  mode: string
  ai: {
    provider: string
    model: string
    api_url: string
    configured: boolean
    hint?: string
  }
}

export interface GenerateResponse {
  run: ApiRun
  items: ApiTestCase[]
}

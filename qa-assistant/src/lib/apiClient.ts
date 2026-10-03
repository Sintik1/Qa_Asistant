/** API helpers that attach Supabase JWT when present. */

import { supabase } from '../lib/supabaseClient'

const apiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() ?? ''

function newRequestId(): string {
  if (typeof crypto !== 'undefined' && 'randomUUID' in crypto) {
    return crypto.randomUUID()
  }
  return `fe-${Date.now()}-${Math.random().toString(16).slice(2)}`
}

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
  }
  if (!headers.has('X-Request-Id')) {
    headers.set('X-Request-Id', newRequestId())
  }

  if (supabase) {
    const { data } = await supabase.auth.getSession()
    const token = data.session?.access_token
    if (token) {
      headers.set('Authorization', `Bearer ${token}`)
    }
  }

  const url = path.startsWith('http')
    ? path
    : `${apiBase.replace(/\/$/, '')}${path.startsWith('/') ? path : `/${path}`}`

  return fetch(url, { ...init, headers })
}

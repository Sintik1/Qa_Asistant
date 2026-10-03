/** API helpers that attach Supabase JWT when present. */

import { supabase } from '../lib/supabaseClient'

const apiBase = (import.meta.env.VITE_API_BASE_URL as string | undefined)?.trim() ?? ''

export async function apiFetch(path: string, init: RequestInit = {}): Promise<Response> {
  const headers = new Headers(init.headers)
  if (!headers.has('Content-Type') && init.body) {
    headers.set('Content-Type', 'application/json')
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

const PROJECT_REF = 'revyywfeeqdmlgrbakpj'

/** Shown when GoTrue/fetch cannot reach Supabase (paused project, VPN, offline). */
export const AUTH_SUPABASE_NETWORK_HINT =
  `Проект Supabase на паузе или недоступен (нет DNS/TLS до *.supabase.co). ` +
  `Откройте https://supabase.com/dashboard/project/${PROJECT_REF} → Restore / Resume, ` +
  `подождите 2–5 минут. Если Clash TUN включён — DIRECT: DOMAIN-SUFFIX,supabase.co.`

export function supabaseDashboardProjectUrl(apiUrl: string | undefined): string | null {
  const raw = (apiUrl || '').trim()
  const match = raw.match(/^https:\/\/([a-z0-9]+)\.supabase\.co/i)
  return match ? `https://supabase.com/dashboard/project/${match[1]}` : null
}

export function messageForAuthError(message: string | null | undefined): string | null {
  if (!message) return null
  if (/failed to fetch|networkerror|load failed|fetch failed/i.test(message)) {
    return AUTH_SUPABASE_NETWORK_HINT
  }
  return message
}

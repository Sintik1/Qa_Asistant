import { describe, expect, it } from 'vitest'
import {
  AUTH_SUPABASE_NETWORK_HINT,
  messageForAuthError,
  supabaseDashboardProjectUrl,
} from './authNetworkError'

describe('messageForAuthError', () => {
  it('maps Failed to fetch to Clash/Supabase network hint', () => {
    expect(messageForAuthError('Failed to fetch')).toBe(AUTH_SUPABASE_NETWORK_HINT)
  })

  it('keeps real Auth API errors', () => {
    expect(messageForAuthError('Invalid login credentials')).toBe(
      'Invalid login credentials',
    )
  })

  it('passes through empty', () => {
    expect(messageForAuthError(null)).toBeNull()
  })

  it('builds dashboard restore URL from API host', () => {
    expect(
      supabaseDashboardProjectUrl('https://revyywfeeqdmlgrbakpj.supabase.co'),
    ).toBe('https://supabase.com/dashboard/project/revyywfeeqdmlgrbakpj')
  })
})

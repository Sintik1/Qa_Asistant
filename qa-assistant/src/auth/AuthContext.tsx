import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react'
import type { Session, User } from '@supabase/supabase-js'
import { isSupabaseConfigured, supabase } from '../lib/supabaseClient'
import { apiBaseUrl } from '../api/client'

type OAuthProvider = 'google' | 'yandex'

type AuthContextValue = {
  configured: boolean
  loading: boolean
  session: Session | null
  user: User | null
  accessToken: string | null
  signIn: (email: string, password: string) => Promise<string | null>
  signUp: (email: string, password: string) => Promise<string | null>
  signInWithOAuth: (provider: OAuthProvider) => Promise<string | null>
  applySessionTokens: (
    accessToken: string,
    refreshToken: string,
  ) => Promise<string | null>
  signOut: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [loading, setLoading] = useState(isSupabaseConfigured)
  const [session, setSession] = useState<Session | null>(null)

  useEffect(() => {
    if (!supabase) {
      setLoading(false)
      return
    }

    let mounted = true
    supabase.auth.getSession().then(({ data }) => {
      if (!mounted) return
      setSession(data.session)
      setLoading(false)
    })

    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next)
      setLoading(false)
    })

    return () => {
      mounted = false
      sub.subscription.unsubscribe()
    }
  }, [])

  const signIn = useCallback(async (email: string, password: string) => {
    if (!supabase) return 'Supabase Auth не настроен (проверьте VITE_SUPABASE_*).'
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    return error?.message ?? null
  }, [])

  const signUp = useCallback(async (email: string, password: string) => {
    if (!supabase) return 'Supabase Auth не настроен (проверьте VITE_SUPABASE_*).'
    const { error } = await supabase.auth.signUp({ email, password })
    return error?.message ?? null
  }, [])

  const applySessionTokens = useCallback(
    async (accessToken: string, refreshToken: string) => {
      if (!supabase) return 'Supabase Auth не настроен (проверьте VITE_SUPABASE_*).'
      const { error } = await supabase.auth.setSession({
        access_token: accessToken,
        refresh_token: refreshToken,
      })
      return error?.message ?? null
    },
    [],
  )

  const signInWithOAuth = useCallback(async (provider: OAuthProvider) => {
    // Google: native Supabase Auth Provider (PKCE + detectSessionInUrl).
    if (provider === 'google') {
      if (!supabase) {
        return 'Supabase Auth не настроен (проверьте VITE_SUPABASE_*).'
      }
      const base = import.meta.env.BASE_URL || '/'
      const callbackPath = `${base.endsWith('/') ? base : `${base}/`}auth/callback`
      const redirectTo = `${window.location.origin}${callbackPath}`
      const { error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
          redirectTo,
          queryParams: { prompt: 'select_account' },
        },
      })
      return error?.message ?? null
    }

    // Yandex: Flask Authorization Code → Supabase Admin session → hash tokens.
    const base = apiBaseUrl()
    if (!base) {
      return 'Не задан VITE_API_BASE_URL для Yandex OAuth (Flask).'
    }
    window.location.assign(`${base}/api/auth/oauth/yandex/start`)
    return null
  }, [])

  const signOut = useCallback(async () => {
    if (!supabase) return
    await supabase.auth.signOut()
  }, [])

  const value = useMemo<AuthContextValue>(
    () => ({
      configured: isSupabaseConfigured,
      loading,
      session,
      user: session?.user ?? null,
      accessToken: session?.access_token ?? null,
      signIn,
      signUp,
      signInWithOAuth,
      applySessionTokens,
      signOut,
    }),
    [loading, session, signIn, signUp, signInWithOAuth, applySessionTokens, signOut],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}

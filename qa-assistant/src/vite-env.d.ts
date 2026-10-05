/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL?: string
  readonly VITE_SUPABASE_URL?: string
  readonly VITE_SUPABASE_ANON_KEY?: string
  /** Public Yandex Metrika counter id (not a secret). */
  readonly VITE_YANDEX_METRIKA_ID?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

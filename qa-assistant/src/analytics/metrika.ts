/**
 * Yandex Metrika helper (CI/CD ДЗ шаг 4).
 * Counter id is public (VITE_*); never put secrets here.
 */

export type MetrikaGoal =
  | 'auth_login'
  | 'auth_signup'
  | 'auth_oauth_start'
  | 'document_upload'
  | 'generate_start'
  | 'generate_success'
  | 'generate_error'
  | 'csv_download'
  | 'chat_send'

type YmFn = {
  (counterId: number, method: string, ...args: unknown[]): void
  a?: unknown[][]
  l?: number
}

declare global {
  interface Window {
    ym?: YmFn
  }
}

const SCRIPT_SRC = 'https://mc.yandex.ru/metrika/tag.js'

let initStarted = false

export function getMetrikaCounterId(): number | null {
  const raw = (import.meta.env.VITE_YANDEX_METRIKA_ID as string | undefined)?.trim()
  if (!raw) return null
  const id = Number(raw)
  return Number.isFinite(id) && id > 0 ? id : null
}

export function isMetrikaEnabled(): boolean {
  return getMetrikaCounterId() !== null
}

/** Load tag.js once and call ym(id, 'init', …). Safe to call multiple times. */
export function initMetrika(): void {
  const id = getMetrikaCounterId()
  if (id === null || typeof window === 'undefined') return
  if (initStarted) return
  initStarted = true

  const ym: YmFn = function (...args: unknown[]) {
    ;(ym.a = ym.a || []).push(args)
  }
  ym.l = Date.now()
  window.ym = ym

  if (!document.querySelector(`script[src="${SCRIPT_SRC}"]`)) {
    const script = document.createElement('script')
    script.async = true
    script.src = SCRIPT_SRC
    document.head.appendChild(script)
  }

  window.ym(id, 'init', {
    clickmap: true,
    trackLinks: true,
    accurateTrackBounce: true,
    webvisor: false,
  })
}

export function trackPageView(url?: string, title?: string): void {
  const id = getMetrikaCounterId()
  if (id === null || typeof window === 'undefined' || !window.ym) return
  const path = url ?? `${window.location.pathname}${window.location.search}`
  window.ym(id, 'hit', path, title ? { title } : undefined)
}

export function trackGoal(
  goal: MetrikaGoal,
  params?: Record<string, string | number | boolean>,
): void {
  const id = getMetrikaCounterId()
  if (id === null || typeof window === 'undefined' || !window.ym) return
  if (params && Object.keys(params).length > 0) {
    window.ym(id, 'reachGoal', goal, params)
  } else {
    window.ym(id, 'reachGoal', goal)
  }
}

/** Test helper — reset module init flag between vitest cases. */
export function __resetMetrikaForTests(): void {
  initStarted = false
}

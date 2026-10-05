import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  __resetMetrikaForTests,
  getMetrikaCounterId,
  initMetrika,
  isMetrikaEnabled,
  trackGoal,
  trackPageView,
} from './metrika'

describe('metrika analytics', () => {
  beforeEach(() => {
    __resetMetrikaForTests()
    vi.unstubAllEnvs()
    document.head.innerHTML = ''
    delete (window as { ym?: unknown }).ym
  })

  it('is disabled without VITE_YANDEX_METRIKA_ID', () => {
    vi.stubEnv('VITE_YANDEX_METRIKA_ID', '')
    expect(getMetrikaCounterId()).toBeNull()
    expect(isMetrikaEnabled()).toBe(false)
    initMetrika()
    expect(document.querySelector('script[src*="mc.yandex.ru"]')).toBeNull()
  })

  it('loads tag and inits when counter id is set', () => {
    vi.stubEnv('VITE_YANDEX_METRIKA_ID', '12345678')
    expect(isMetrikaEnabled()).toBe(true)
    initMetrika()
    const script = document.querySelector(
      'script[src="https://mc.yandex.ru/metrika/tag.js"]',
    )
    expect(script).toBeTruthy()
    expect(typeof window.ym).toBe('function')
    expect(window.ym!.a?.length).toBeGreaterThan(0)
    expect(window.ym!.a![0][0]).toBe(12345678)
    expect(window.ym!.a![0][1]).toBe('init')
  })

  it('trackGoal / trackPageView call ym when enabled', () => {
    vi.stubEnv('VITE_YANDEX_METRIKA_ID', '999')
    const ym = vi.fn()
    window.ym = ym as typeof window.ym

    trackPageView('/auth')
    trackGoal('generate_success', { cases: 3 })

    expect(ym).toHaveBeenCalledWith(999, 'hit', '/auth', undefined)
    expect(ym).toHaveBeenCalledWith(999, 'reachGoal', 'generate_success', {
      cases: 3,
    })
  })

  it('trackGoal is a no-op without counter id', () => {
    vi.stubEnv('VITE_YANDEX_METRIKA_ID', '')
    const ym = vi.fn()
    window.ym = ym as typeof window.ym
    trackGoal('auth_login')
    expect(ym).not.toHaveBeenCalled()
  })
})

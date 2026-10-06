import { describe, expect, it, vi, beforeEach, afterEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { AuthCallbackPage } from './AuthCallbackPage'

vi.mock('../analytics/metrika', () => ({
  trackGoal: vi.fn(),
}))

const applySessionTokens = vi.fn()

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({
    configured: true,
    loading: false,
    user: null,
    applySessionTokens,
    session: null,
    accessToken: null,
  }),
}))

describe('AuthCallbackPage OAuth errors', () => {
  const originalLocation = window.location

  beforeEach(() => {
    applySessionTokens.mockReset()
  })

  afterEach(() => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: originalLocation,
    })
  })

  it('shows oauth_message from query on first render (step 8 fix)', () => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: {
        ...originalLocation,
        search: '?oauth_error=YANDEX_STATE&oauth_message=Invalid%20state',
        hash: '',
        pathname: '/auth/callback',
      },
    })

    render(
      <MemoryRouter initialEntries={['/auth/callback?oauth_error=YANDEX_STATE']}>
        <AuthCallbackPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('Invalid state')).toBeInTheDocument()
    expect(applySessionTokens).not.toHaveBeenCalled()
  })

  it('falls back to oauth_error code when message missing', () => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: {
        ...originalLocation,
        search: '?oauth_error=YANDEX_STATE',
        hash: '',
        pathname: '/auth/callback',
      },
    })

    render(
      <MemoryRouter>
        <AuthCallbackPage />
      </MemoryRouter>,
    )

    expect(screen.getByText('YANDEX_STATE')).toBeInTheDocument()
  })
})

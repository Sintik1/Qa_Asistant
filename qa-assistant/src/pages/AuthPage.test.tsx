import { describe, expect, it, vi, beforeEach } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { AuthPage } from './AuthPage'

const signInWithOAuth = vi.fn()

vi.mock('../auth/AuthContext', () => ({
  useAuth: () => ({
    configured: true,
    loading: false,
    user: null,
    signIn: vi.fn(),
    signUp: vi.fn(),
    signInWithOAuth,
    signOut: vi.fn(),
    applySessionTokens: vi.fn(),
    session: null,
    accessToken: null,
  }),
}))

vi.mock('../api/client', () => ({
  apiBaseUrl: () => 'http://127.0.0.1:5001',
  isApiConfigured: () => true,
}))

describe('AuthPage OAuth', () => {
  beforeEach(() => {
    signInWithOAuth.mockReset()
    signInWithOAuth.mockResolvedValue(null)
  })

  it('starts Google OAuth on button click', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>,
    )
    await user.click(screen.getByRole('button', { name: /Войти через Google/i }))
    expect(signInWithOAuth).toHaveBeenCalledWith('google')
  })

  it('starts Yandex OAuth on button click', async () => {
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>,
    )
    await user.click(screen.getByRole('button', { name: /Войти через Yandex/i }))
    expect(signInWithOAuth).toHaveBeenCalledWith('yandex')
  })

  it('shows OAuth error message', async () => {
    signInWithOAuth.mockResolvedValue('provider unavailable')
    const user = userEvent.setup()
    render(
      <MemoryRouter>
        <AuthPage />
      </MemoryRouter>,
    )
    await user.click(screen.getByRole('button', { name: /Войти через Google/i }))
    expect(await screen.findByText('provider unavailable')).toBeInTheDocument()
  })
})

import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { AiProviderSwitch } from './AiProviderSwitch'

const getAiProvider = vi.fn()
const setAiProvider = vi.fn()

vi.mock('../../api/settings', () => ({
  getAiProvider: (...args: unknown[]) => getAiProvider(...args),
  setAiProvider: (...args: unknown[]) => setAiProvider(...args),
}))

describe('AiProviderSwitch', () => {
  beforeEach(() => {
    getAiProvider.mockReset()
    setAiProvider.mockReset()
  })

  it('shows local as active and switches to Leopold', async () => {
    const user = userEvent.setup()
    getAiProvider.mockResolvedValue({
      provider: 'ollama',
      model: 'qwen2.5:1.5b',
      configured: true,
    })
    setAiProvider.mockResolvedValue({
      provider: 'leopold',
      model: 'Qwen/Qwen3-Next-80B-A3B-Instruct-FP8',
      configured: true,
    })

    render(<AiProviderSwitch />)

    const local = await screen.findByRole('button', { name: 'Локально' })
    expect(local).toHaveAttribute('aria-pressed', 'true')

    await user.click(screen.getByRole('button', { name: 'Leopold' }))
    expect(setAiProvider).toHaveBeenCalledWith('leopold')
    expect(await screen.findByRole('button', { name: 'Leopold' })).toHaveAttribute(
      'aria-pressed',
      'true',
    )
  })
})

import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { GenerationAlerts } from './GenerationAlerts'
import { ERROR_MESSAGES } from '../../utils/constants'

describe('GenerationAlerts', () => {
  const noop = {
    onOpenSettings: vi.fn(),
    onClearGenerationError: vi.fn(),
    onClearRequirements: vi.fn(),
    onRetry: vi.fn(),
    onClearWarning: vi.fn(),
  }

  it('shows missing-token alert with settings CTA', async () => {
    const user = userEvent.setup()
    const onOpenSettings = vi.fn()
    render(
      <GenerationAlerts
        {...noop}
        formError={ERROR_MESSAGES.MISSING_TOKEN}
        generationError={null}
        warning={null}
        onOpenSettings={onOpenSettings}
      />,
    )
    expect(screen.getByRole('alert')).toHaveTextContent(
      ERROR_MESSAGES.MISSING_TOKEN,
    )
    await user.click(screen.getByRole('button', { name: 'Настроить токен' }))
    expect(onOpenSettings).toHaveBeenCalledTimes(1)
  })

  it('routes NO_REQUIREMENTS action to clear file + error', async () => {
    const user = userEvent.setup()
    const onClearRequirements = vi.fn()
    const onClearGenerationError = vi.fn()
    const onRetry = vi.fn()
    render(
      <GenerationAlerts
        {...noop}
        formError={null}
        generationError={ERROR_MESSAGES.NO_REQUIREMENTS}
        warning={null}
        onClearRequirements={onClearRequirements}
        onClearGenerationError={onClearGenerationError}
        onRetry={onRetry}
      />,
    )
    await user.click(
      screen.getByRole('button', { name: 'Загрузить другой файл' }),
    )
    expect(onClearRequirements).toHaveBeenCalledTimes(1)
    expect(onClearGenerationError).toHaveBeenCalledTimes(1)
    expect(onRetry).not.toHaveBeenCalled()
  })

  it('retries on generic generation error', async () => {
    const user = userEvent.setup()
    const onRetry = vi.fn()
    render(
      <GenerationAlerts
        {...noop}
        formError={null}
        generationError={ERROR_MESSAGES.API_UNAVAILABLE}
        warning={null}
        onRetry={onRetry}
      />,
    )
    await user.click(screen.getByRole('button', { name: 'Повторить' }))
    expect(onRetry).toHaveBeenCalledTimes(1)
  })
})

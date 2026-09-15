import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ErrorMessage } from './ErrorMessage'
import { ERROR_MESSAGES } from '../../utils/constants'

describe('ErrorMessage', () => {
  it('exposes TZ message via role=alert', () => {
    render(<ErrorMessage message={ERROR_MESSAGES.MISSING_TOKEN} />)
    expect(screen.getByRole('alert')).toHaveTextContent(
      ERROR_MESSAGES.MISSING_TOKEN,
    )
  })

  it('renders action button and invokes handler', async () => {
    const user = userEvent.setup()
    const onAction = vi.fn()
    render(
      <ErrorMessage
        message={ERROR_MESSAGES.MISSING_TOKEN}
        actionLabel="Настроить токен"
        onAction={onAction}
      />,
    )
    await user.click(screen.getByRole('button', { name: 'Настроить токен' }))
    expect(onAction).toHaveBeenCalledTimes(1)
  })

  it('hides action when only label is provided', () => {
    render(
      <ErrorMessage
        message={ERROR_MESSAGES.INVALID_FORMAT}
        actionLabel="Игнорировать"
      />,
    )
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})

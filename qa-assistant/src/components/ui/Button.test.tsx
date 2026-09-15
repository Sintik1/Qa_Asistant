import { describe, expect, it, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

describe('Button', () => {
  it('renders children and defaults to type=button', () => {
    render(<Button>Сохранить</Button>)
    const button = screen.getByRole('button', { name: 'Сохранить' })
    expect(button).toHaveAttribute('type', 'button')
  })

  it('calls onClick when enabled', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(
      <Button onClick={onClick} variant="success">
        Скачать CSV
      </Button>,
    )
    await user.click(screen.getByRole('button', { name: 'Скачать CSV' }))
    expect(onClick).toHaveBeenCalledTimes(1)
  })

  it('does not call onClick when disabled', async () => {
    const user = userEvent.setup()
    const onClick = vi.fn()
    render(
      <Button onClick={onClick} disabled>
        Генерировать
      </Button>,
    )
    await user.click(screen.getByRole('button', { name: 'Генерировать' }))
    expect(onClick).not.toHaveBeenCalled()
  })
})

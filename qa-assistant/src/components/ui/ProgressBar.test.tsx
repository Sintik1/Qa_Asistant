import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { ProgressBar } from './ProgressBar'

describe('ProgressBar', () => {
  it('renders determinate progress with aria value', () => {
    render(<ProgressBar label="Генерация тест-кейсов..." value={40} />)
    expect(screen.getByText('Генерация тест-кейсов...')).toBeInTheDocument()
    const bar = screen.getByRole('progressbar', {
      name: 'Генерация тест-кейсов...',
    })
    expect(bar).toHaveAttribute('aria-valuenow', '40')
    expect(bar).toHaveStyle({ width: '40%' })
  })

  it('omits aria-valuenow for indeterminate progress', () => {
    render(<ProgressBar label="Извлечение текста." />)
    const bar = screen.getByRole('progressbar', { name: 'Извлечение текста.' })
    expect(bar).not.toHaveAttribute('aria-valuenow')
  })
})

import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { PageHeader } from './PageHeader'

describe('PageHeader', () => {
  it('renders title as heading', () => {
    render(<PageHeader title="Написание тест-кейсов" />)
    expect(
      screen.getByRole('heading', { name: 'Написание тест-кейсов' }),
    ).toBeInTheDocument()
  })

  it('renders optional description', () => {
    render(
      <PageHeader
        title="Настройки"
        description="API-токен для генерации"
      />,
    )
    expect(screen.getByText('API-токен для генерации')).toBeInTheDocument()
  })
})

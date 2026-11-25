import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MarkdownAnswer } from './MarkdownAnswer'

describe('MarkdownAnswer', () => {
  it('renders a Confluence ordered list and a heading', () => {
    render(
      <MarkdownAnswer
        text={'## Инструкция подключения\n\n1. Создать заказ\n2. Отправить на исполнение'}
      />,
    )
    expect(screen.getByText('Инструкция подключения')).toBeInTheDocument()
    const items = screen.getAllByRole('listitem')
    expect(items.map((item) => item.textContent)).toEqual([
      'Создать заказ',
      'Отправить на исполнение',
    ])
    expect(screen.getByRole('list').tagName).toBe('OL')
  })

  it('renders a Confluence markdown table', () => {
    render(
      <MarkdownAnswer
        text={
          '| **Система** | ip и порт |\n| --- | --- |\n| активатор->SDP | 112.000.000:8080 |\n| активатор->CRM | Активация<br>Деактивация |'
        }
      />,
    )
    expect(screen.getByRole('table')).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'Система' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: 'активатор->SDP' })).toBeInTheDocument()
    expect(screen.getByRole('cell', { name: /Активация/ })).toHaveTextContent('Деактивация')
  })

  it('keeps consecutive Confluence paragraphs apart', () => {
    render(
      <MarkdownAnswer
        text={'Здесь информация по Лицей\nПодключение происходит через CRM и ЛК\n\nСервисы которые используются'}
      />,
    )
    expect(screen.getByText('Здесь информация по Лицей').tagName).toBe('P')
    expect(screen.getByText('Подключение происходит через CRM и ЛК').tagName).toBe('P')
    expect(screen.getByText('Сервисы которые используются').tagName).toBe('P')
  })
})

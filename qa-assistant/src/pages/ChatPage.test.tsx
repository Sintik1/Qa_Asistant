import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { ChatPage } from './ChatPage'

const chatRequirements = vi.fn()

vi.mock('../api/chat', () => ({
  chatRequirements: (...args: unknown[]) => chatRequirements(...args),
}))

describe('ChatPage', () => {
  beforeEach(() => {
    chatRequirements.mockReset()
  })

  it('asks RAG and renders answer with citations', async () => {
    const user = userEvent.setup()
    chatRequirements.mockResolvedValue({
      answer: 'Рассрочка на 24 месяца.',
      citations: [
        {
          document_id: 'doc-1',
          section_path: 'Основные требования',
          similarity: 0.91,
        },
      ],
    })

    render(<ChatPage />)

    await user.type(
      screen.getByPlaceholderText(/условия рассрочки/i),
      'Какой срок рассрочки?',
    )
    await user.click(screen.getByRole('button', { name: 'Спросить' }))

    await waitFor(() => {
      expect(chatRequirements).toHaveBeenCalledWith({
        question: 'Какой срок рассрочки?',
        document_id: undefined,
      })
    })
    expect(await screen.findByText(/24 месяца/i)).toBeInTheDocument()
    expect(screen.getByText('Основные требования')).toBeInTheDocument()
  })

  it('shows API error via alert', async () => {
    const user = userEvent.setup()
    chatRequirements.mockRejectedValue({
      response: {
        status: 502,
        data: {
          error: { code: 'API_EMPTY', message: 'Сервис анализа не сгенерировал ответ' },
        },
      },
    })

    render(<ChatPage />)
    await user.type(
      screen.getByPlaceholderText(/условия рассрочки/i),
      'Есть ли акция?',
    )
    await user.click(screen.getByRole('button', { name: 'Спросить' }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })
})

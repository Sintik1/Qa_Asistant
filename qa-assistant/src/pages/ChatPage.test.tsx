import { beforeEach, describe, expect, it, vi } from 'vitest'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import userEvent from '@testing-library/user-event'
import { ChatPage } from './ChatPage'

const chatRequirements = vi.fn()
const syncConfluenceSpace = vi.fn()
const listDocuments = vi.fn()
const getHealth = vi.fn()

vi.mock('../api/chat', () => ({
  chatRequirements: (...args: unknown[]) => chatRequirements(...args),
  syncConfluenceSpace: (...args: unknown[]) => syncConfluenceSpace(...args),
}))

vi.mock('../api/documents', () => ({
  listDocuments: (...args: unknown[]) => listDocuments(...args),
}))

vi.mock('../api/settings', () => ({
  getHealth: (...args: unknown[]) => getHealth(...args),
}))

vi.mock('../analytics/metrika', () => ({
  trackGoal: vi.fn(),
}))

function renderChat() {
  return render(
    <MemoryRouter>
      <ChatPage />
    </MemoryRouter>,
  )
}

describe('ChatPage', () => {
  beforeEach(() => {
    chatRequirements.mockReset()
    syncConfluenceSpace.mockReset()
    listDocuments.mockResolvedValue([
      {
        id: 'doc-1',
        user_id: 'u1',
        original_filename: 'reqs.md',
        mime_type: 'text/markdown',
        size_bytes: 12,
        storage_path: 'x',
        status: 'parsed',
        created_at: null,
      },
    ])
    getHealth.mockResolvedValue({
      status: 'ok',
      api: 'qa-assistant',
      mode: 'hybrid-c',
      ai: { provider: 'ollama', model: 'qwen', api_url: 'x', configured: true },
      rag: { enabled: true, embedding_model: 'nomic-embed-text' },
    })
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
          source_kind: 'requirement',
        },
      ],
    })

    renderChat()

    expect(await screen.findByText(/RAG: включён/i)).toBeInTheDocument()

    await user.type(
      screen.getByPlaceholderText(/условия рассрочки/i),
      'Какой срок рассрочки?',
    )
    await user.click(screen.getByRole('button', { name: 'Спросить' }))

    await waitFor(() => {
      expect(chatRequirements).toHaveBeenCalledWith({
        question: 'Какой срок рассрочки?',
        document_id: undefined,
        include_cases: true,
      })
    })
    expect(await screen.findByText(/24 месяца/i)).toBeInTheDocument()
    expect(screen.getByText(/Основные требования/)).toBeInTheDocument()
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

    renderChat()
    await user.type(
      screen.getByPlaceholderText(/условия рассрочки/i),
      'Есть ли акция?',
    )
    await user.click(screen.getByRole('button', { name: 'Спросить' }))

    expect(await screen.findByRole('alert')).toBeInTheDocument()
  })

  it('scopes the question to a document and skips case index', async () => {
    const user = userEvent.setup()
    chatRequirements.mockResolvedValue({ answer: 'Только из документа.', citations: [] })
    renderChat()

    await screen.findByRole('option', { name: 'reqs.md' })
    await user.selectOptions(screen.getByLabelText(/Документ/i), 'doc-1')
    await user.click(
      screen.getByRole('checkbox', { name: /шаблонах и проиндексированных кейсах/i }),
    )
    await user.type(screen.getByLabelText('Вопрос'), 'Что в каталоге?')
    await user.click(screen.getByRole('button', { name: 'Спросить' }))

    await waitFor(() => {
      expect(chatRequirements).toHaveBeenCalledWith({
        question: 'Что в каталоге?',
        document_id: 'doc-1',
        include_cases: false,
      })
    })
    expect(await screen.findByText('Только из документа.')).toBeInTheDocument()
  })

  it('renders a case citation with similarity and preview', async () => {
    const user = userEvent.setup()
    chatRequirements.mockResolvedValue({
      answer: 'По шаблону 24 месяца.',
      citations: [
        {
          document_id: 'case-1',
          section_path: 'Рассрочка 24',
          similarity: 0.5,
          source_kind: 'case',
          preview: 'Выбрать 24 месяца',
        },
      ],
    })
    renderChat()
    await user.type(screen.getByLabelText('Вопрос'), 'Срок рассрочки?')
    await user.click(screen.getByRole('button', { name: 'Спросить' }))

    expect(await screen.findByText('Кейс: Рассрочка 24')).toBeInTheDocument()
    expect(screen.getByText(/сходство 0\.500/)).toBeInTheDocument()
    expect(screen.getByText('Выбрать 24 месяца')).toBeInTheDocument()
  })

  it('shows disabled RAG, embedding hint, and blocks a short question', async () => {
    getHealth.mockResolvedValue({
      status: 'ok',
      api: 'qa-assistant',
      mode: 'hybrid-c',
      ai: { provider: 'leopold', model: 'Qwen', api_url: 'x', configured: true },
      rag: { enabled: false, embedding_model: 'hash-v1' },
    })
    renderChat()

    expect(await screen.findByText(/RAG: выключен/i)).toBeInTheDocument()
    expect(screen.getByText(/эмбеддинги: hash-v1/i)).toBeInTheDocument()

    const ask = screen.getByRole('button', { name: 'Спросить' })
    expect(ask).toBeDisabled()
    await userEvent.setup().type(screen.getByLabelText('Вопрос'), 'а')
    expect(ask).toBeDisabled()
    expect(chatRequirements).not.toHaveBeenCalled()
  })

  it('shows the upload link when the document index is empty', async () => {
    listDocuments.mockResolvedValue([])
    renderChat()
    expect(await screen.findByRole('link', { name: 'Загрузить требования' })).toHaveAttribute(
      'href',
      '/',
    )
    expect(screen.getByText(/Индекс пуст/i)).toBeInTheDocument()
  })

  it('shows unknown RAG status when health fails and a searching state while waiting', async () => {
    const user = userEvent.setup()
    getHealth.mockRejectedValue(new Error('offline'))
    let finish: (value: { answer: string; citations: [] }) => void = () => {}
    chatRequirements.mockImplementation(
      () =>
        new Promise((resolve) => {
          finish = resolve
        }),
    )
    renderChat()
    expect(await screen.findByText(/RAG: статус неизвестен/i)).toBeInTheDocument()

    await user.type(screen.getByLabelText('Вопрос'), 'Где таблица Email?')
    await user.click(screen.getByRole('button', { name: 'Спросить' }))
    expect(await screen.findByRole('status')).toHaveTextContent(/Ищу в базе/i)
    expect(screen.getByRole('button', { name: 'Думаю…' })).toBeDisabled()

    finish({ answer: 'Email — string.', citations: [] })
    expect(await screen.findByText('Email — string.')).toBeInTheDocument()
  })

  it('syncs a Confluence space into the document list', async () => {
    const user = userEvent.setup()
    syncConfluenceSpace.mockResolvedValue({
      space: 'QA',
      pages: 2,
      indexed: 1,
      skipped: 1,
    })
    listDocuments
      .mockResolvedValueOnce([])
      .mockResolvedValueOnce([
        {
          id: 'conf-1',
          user_id: 'u1',
          original_filename: 'Рассрочка.md',
          mime_type: 'text/html',
          size_bytes: 20,
          storage_path: 'confluence/QA/1@v3',
          status: 'extracted',
          created_at: null,
        },
      ])
    renderChat()
    await user.click(screen.getByRole('button', { name: 'Синхронизировать Confluence' }))
    expect(await screen.findByText(/проиндексировано 1/i)).toBeInTheDocument()
    expect(await screen.findByRole('option', { name: 'Рассрочка.md' })).toBeInTheDocument()
    expect(syncConfluenceSpace).toHaveBeenCalledOnce()
  })
})

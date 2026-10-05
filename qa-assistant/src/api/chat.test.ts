import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiJson = vi.fn()

vi.mock('./client', () => ({
  apiJson: (...args: unknown[]) => apiJson(...args),
}))

describe('chatRequirements', () => {
  beforeEach(() => {
    apiJson.mockReset()
  })

  it('posts question and optional document_id', async () => {
    apiJson.mockResolvedValue({
      answer: '24 месяца',
      citations: [{ document_id: 'd1', section_path: '1 Основные' }],
    })
    const { chatRequirements } = await import('./chat')
    const res = await chatRequirements({
      question: 'Срок рассрочки?',
      document_id: 'd1',
    })
    expect(apiJson).toHaveBeenCalledWith('/api/chat', {
      method: 'POST',
      body: JSON.stringify({
        question: 'Срок рассрочки?',
        document_id: 'd1',
      }),
    })
    expect(res.answer).toContain('24')
    expect(res.citations).toHaveLength(1)
  })
})

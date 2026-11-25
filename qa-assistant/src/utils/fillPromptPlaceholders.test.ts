import { describe, expect, it } from 'vitest'
import {
  fillPromptPlaceholders,
  promptHasRequirementsMarker,
} from './fillPromptPlaceholders'

describe('fillPromptPlaceholders', () => {
  it('replaces the requirements marker and keeps the rest of the prompt', () => {
    const filled = fillPromptPlaceholders(
      'Инструкция\n*Тут текст требований*\nДальше',
      '3. CRM\n1. Проверить тариф',
    )
    expect(filled).toBe('Инструкция\n3. CRM\n1. Проверить тариф\nДальше')
    expect(filled.includes('*Тут текст требований*')).toBe(false)
  })

  it('leaves a prompt without a marker unchanged', () => {
    expect(fillPromptPlaceholders('Только инструкция', 'текст файла')).toBe(
      'Только инструкция',
    )
  })

  it('detects the marker regardless of letter case', () => {
    expect(promptHasRequirementsMarker('смотри *тут текст требований*')).toBe(true)
    expect(promptHasRequirementsMarker('без маркера')).toBe(false)
  })
})

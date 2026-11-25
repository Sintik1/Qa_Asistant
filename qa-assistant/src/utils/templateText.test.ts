import { describe, expect, it } from 'vitest'
import { combineTemplateSources } from './templateText'

describe('combineTemplateSources', () => {
  it('returns empty when both sources are blank', () => {
    expect(combineTemplateSources('  ', '\n')).toBe('')
  })

  it('keeps a single source', () => {
    expect(combineTemplateSources('шаблон', '')).toBe('шаблон')
    expect(combineTemplateSources('', 'из файла')).toBe('из файла')
  })

  it('joins both sources without dropping either', () => {
    expect(combineTemplateSources('библиотека', 'файл')).toBe('библиотека\n\nфайл')
  })
})

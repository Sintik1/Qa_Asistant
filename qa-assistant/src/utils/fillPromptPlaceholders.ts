const REQUIREMENTS_PLACEHOLDERS = [
  '*Тут текст требований*',
  '*Тут вставить текст требований*',
  '*Тут вставить текстовый формат документа*',
  '*Тут вставить документ*',
  '<ТУТ БУДЕТ ВСТАВЛЕН ТЕКСТ ДОКУМЕНТА>',
  '<ТУТ БУДЕТ ВСТАВЛЕН ТЕКСТ ТРЕБОВАНИЙ>',
]

const TEMPLATE_PLACEHOLDERS = [
  '*Тут вставить шаблон*',
  '*Вставить шаблон*',
  '*Тут текст шаблонов*',
  '*Тут вставить шаблоны*',
  '*Тут вставить шаблоны сценариев*',
  '*Тут вставить шаблон сценариев*',
]

/** Put parsed document or template text in place of the known markers. */
export function fillPromptPlaceholders(
  prompt: string,
  requirementsText: string,
  templateText = '',
): string {
  let filled = prompt
  const requirements = requirementsText.trim()
  const template = templateText.trim()
  if (requirements) {
    filled = replaceMarkers(filled, REQUIREMENTS_PLACEHOLDERS, requirements)
  }
  if (template) {
    filled = replaceMarkers(filled, TEMPLATE_PLACEHOLDERS, template)
  }
  return filled
}

export function promptHasRequirementsMarker(prompt: string): boolean {
  return REQUIREMENTS_PLACEHOLDERS.some((marker) =>
    prompt.toLowerCase().includes(marker.toLowerCase()),
  )
}

function replaceMarkers(text: string, markers: string[], value: string): string {
  let filled = text
  for (const marker of markers) {
    const pattern = new RegExp(escapeRegExp(marker), 'gi')
    filled = filled.replace(pattern, () => value)
  }
  return filled
}

function escapeRegExp(value: string): string {
  return value.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

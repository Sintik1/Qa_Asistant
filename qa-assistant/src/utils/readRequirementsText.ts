/** Client-side text for thin generate (full extract stays on server later). */

export async function readRequirementsText(file: File): Promise<string> {
  const lower = file.name.toLowerCase()
  if (lower.endsWith('.md') || lower.endsWith('.txt')) {
    const text = (await file.text()).trim()
    return text
  }

  return (
    `Файл требований: ${file.name} (${file.size} bytes).\n` +
    'Сгенерируй типовые функциональные тест-кейсы для документа требований ПО.'
  )
}

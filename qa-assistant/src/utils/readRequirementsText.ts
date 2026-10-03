/**
 * @deprecated Prefer server extract via `uploadDocument` (`POST /api/documents/upload`).
 * Kept for offline/unit helpers if needed.
 */
export async function readRequirementsText(file: File): Promise<string> {
  const lower = file.name.toLowerCase()
  if (lower.endsWith('.md') || lower.endsWith('.txt')) {
    return (await file.text()).trim()
  }
  throw new Error(
    'Client-side extract for PDF/DOCX/DOC removed — use POST /api/documents/upload',
  )
}

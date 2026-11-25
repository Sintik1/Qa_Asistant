/** Join a saved template and a one-run file. Empty parts are omitted. */
export function combineTemplateSources(libraryText: string, fileText: string): string {
  return [libraryText.trim(), fileText.trim()].filter(Boolean).join('\n\n')
}

export const TEMPLATE_TEXT_MAX = 20_000

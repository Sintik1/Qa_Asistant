/**
 * Имя CSV из названия задачи или имени файла требований.
 * Подсказка Figma: «Тест кейсы_<название>.csv»
 */
export function buildCsvFileName(
  taskName: string,
  requirementsFileName?: string,
): string {
  const raw =
    taskName.trim() ||
    (requirementsFileName
      ? requirementsFileName.replace(/\.[^.]+$/, '')
      : 'result')

  const safe = raw.replace(/[\\/:*?"<>|]+/g, '_').trim() || 'result'
  return `Тест кейсы_${safe}.csv`
}

/**
 * Builds download CSV name from task name or requirements file name.
 * Figma hint: «Тест кейсы_<название>.csv»
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

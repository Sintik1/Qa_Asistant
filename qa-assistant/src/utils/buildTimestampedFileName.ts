/**
 * Имя файла экспорта по ТЗ:
 * `test_cases_YYYYMMDD_HHMMSS.csv` / `.docx`
 */
export function buildTimestampedFileName(
  extension: 'csv' | 'docx',
  date: Date = new Date(),
): string {
  const pad = (n: number) => String(n).padStart(2, '0')
  const yyyy = date.getFullYear()
  const mm = pad(date.getMonth() + 1)
  const dd = pad(date.getDate())
  const hh = pad(date.getHours())
  const mi = pad(date.getMinutes())
  const ss = pad(date.getSeconds())
  return `test_cases_${yyyy}${mm}${dd}_${hh}${mi}${ss}.${extension}`
}

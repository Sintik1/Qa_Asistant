import { Button } from '../ui/Button'
import type { GenerationResult } from '../../types'
import { downloadDocx } from '../../utils/docxExport'

interface GenerationResultsProps {
  result: GenerationResult
  onRegenerateClick: () => void
  onDownloadCsv: () => void
}

/**
 * Действия после генерации: CSV (M3), DOCX (S2), вход в перегенерацию (S1).
 */
export function GenerationResults({
  result,
  onRegenerateClick,
  onDownloadCsv,
}: GenerationResultsProps) {
  const count = result.cases.length

  return (
    <section
      className="space-y-4 rounded-md border border-green-200 bg-green-50 p-4"
      aria-live="polite"
    >
      <div>
        <h2 className="text-sm font-semibold text-green-900">
          Генерация завершена
        </h2>
        <p className="text-sm text-green-800">
          Сформировано тест-кейсов: {count}. Колонки CSV: Name, Status, Step,
          Expected Result.
        </p>
      </div>

      <div className="overflow-x-auto rounded-md border border-green-200 bg-white">
        <table className="min-w-full text-left text-sm">
          <thead className="bg-slate-50 text-slate-700">
            <tr>
              <th className="px-3 py-2 font-medium">Name</th>
              <th className="px-3 py-2 font-medium">Status</th>
              <th className="px-3 py-2 font-medium">Step</th>
              <th className="px-3 py-2 font-medium">Expected Result</th>
            </tr>
          </thead>
          <tbody>
            {result.cases.map((item) => (
              <tr key={item.name} className="border-t border-slate-100 align-top">
                <td className="px-3 py-2 text-slate-900">{item.name}</td>
                <td className="px-3 py-2 text-slate-700">{item.status}</td>
                <td className="max-w-xs whitespace-pre-wrap px-3 py-2 text-slate-700">
                  {item.step}
                </td>
                <td className="max-w-xs whitespace-pre-wrap px-3 py-2 text-slate-700">
                  {item.expectedResult}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="flex flex-wrap gap-3">
        <Button
          type="button"
          variant="success"
          className="w-auto"
          onClick={onDownloadCsv}
        >
          Скачать CSV
        </Button>
        <Button
          type="button"
          variant="secondary"
          className="w-auto"
          onClick={() => downloadDocx(result.cases, result.generatedAt)}
        >
          Скачать DOCX
        </Button>
        <Button
          type="button"
          variant="secondary"
          className="w-auto bg-slate-700 hover:bg-slate-800"
          onClick={onRegenerateClick}
        >
          Перегенерировать с настройками
        </Button>
      </div>
    </section>
  )
}

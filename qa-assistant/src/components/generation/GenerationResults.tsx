import { Button } from '../ui/Button'
import { useBreakpoint } from '../../hooks/useBreakpoint'
import type { GenerationResult, TestCase } from '../../types'
import { downloadDocx } from '../../utils/docxExport'

interface GenerationResultsProps {
  result: GenerationResult
  onRegenerateClick: () => void
  onDownloadCsv: () => void
}

function CaseCard({ item }: { item: TestCase }) {
  return (
    <article className="app-case-cards__item">
      <div>
        <p className="app-case-cards__label">Name</p>
        <p className="text-sm font-medium text-slate-900">{item.name}</p>
      </div>
      <div>
        <p className="app-case-cards__label">Status</p>
        <p className="text-sm text-slate-700">{item.status}</p>
      </div>
      <div>
        <p className="app-case-cards__label">Step</p>
        <p className="whitespace-pre-wrap text-sm text-slate-700">{item.step}</p>
      </div>
      <div>
        <p className="app-case-cards__label">Expected Result</p>
        <p className="whitespace-pre-wrap text-sm text-slate-700">
          {item.expectedResult}
        </p>
      </div>
    </article>
  )
}

/**
 * Действия после генерации: CSV (M3), DOCX (S2), вход в перегенерацию (S1).
 * На &lt; md — карточки; на md+ — таблица со scroll-x.
 */
export function GenerationResults({
  result,
  onRegenerateClick,
  onDownloadCsv,
}: GenerationResultsProps) {
  const { isMdUp } = useBreakpoint()
  const count = result.cases.length

  return (
    <section
      className="space-y-4 rounded-md border border-green-200 bg-green-50 p-3 sm:p-4"
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

      {isMdUp ? (
        <div className="app-table-scroll rounded-md border border-green-200 bg-white">
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
                <tr
                  key={item.name}
                  className="border-t border-slate-100 align-top"
                >
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
      ) : (
        <div className="app-case-cards" role="list">
          {result.cases.map((item) => (
            <div key={item.name} role="listitem">
              <CaseCard item={item} />
            </div>
          ))}
        </div>
      )}

      <div className="app-actions">
        <Button type="button" variant="success" onClick={onDownloadCsv}>
          Скачать CSV
        </Button>
        <Button
          type="button"
          variant="secondary"
          onClick={() => downloadDocx(result.cases, result.generatedAt)}
        >
          Скачать DOCX
        </Button>
        <Button
          type="button"
          variant="secondary"
          className="bg-slate-700 hover:bg-slate-800"
          onClick={onRegenerateClick}
        >
          Перегенерировать с настройками
        </Button>
      </div>
    </section>
  )
}

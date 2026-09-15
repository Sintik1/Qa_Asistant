import { Button } from '../ui/Button'
import type { GenerationResult, TestCase } from '../../types'
import { downloadDocx } from '../../utils/docxExport'

interface GenerationResultsProps {
  result: GenerationResult
  onRegenerateClick: () => void
  onDownloadCsv: () => void
}

const CASE_FIELDS = [
  { key: 'name', label: 'Name', preWrap: false },
  { key: 'status', label: 'Status', preWrap: false },
  { key: 'step', label: 'Step', preWrap: true },
  { key: 'expectedResult', label: 'Expected Result', preWrap: true },
] as const satisfies ReadonlyArray<{
  key: keyof TestCase
  label: string
  preWrap: boolean
}>

function CaseCard({ item }: { item: TestCase }) {
  return (
    <article className="app-case-cards__item" role="listitem">
      {CASE_FIELDS.map((field) => (
        <div key={field.key}>
          <p className="app-case-cards__label">{field.label}</p>
          <p
            className={
              field.preWrap
                ? 'whitespace-pre-wrap text-sm text-slate-700'
                : field.key === 'name'
                  ? 'text-sm font-medium text-slate-900'
                  : 'text-sm text-slate-700'
            }
          >
            {item[field.key]}
          </p>
        </div>
      ))}
    </article>
  )
}

/**
 * Действия после генерации: CSV (M3), DOCX (S2), вход в перегенерацию (S1).
 * На &lt; md — карточки; на md+ — таблица со scroll-x (переключение через CSS, без JS).
 */
export function GenerationResults({
  result,
  onRegenerateClick,
  onDownloadCsv,
}: GenerationResultsProps) {
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

      <div className="app-results-table">
        <div className="app-table-scroll rounded-md border border-green-200 bg-white">
          <table className="min-w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-700">
              <tr>
                {CASE_FIELDS.map((field) => (
                  <th key={field.key} className="px-3 py-2 font-medium">
                    {field.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {result.cases.map((item) => (
                <tr
                  key={item.name}
                  className="border-t border-slate-100 align-top"
                >
                  {CASE_FIELDS.map((field) => (
                    <td
                      key={field.key}
                      className={
                        field.preWrap
                          ? 'max-w-xs whitespace-pre-wrap px-3 py-2 text-slate-700'
                          : field.key === 'name'
                            ? 'px-3 py-2 text-slate-900'
                            : 'px-3 py-2 text-slate-700'
                      }
                    >
                      {item[field.key]}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="app-case-cards" role="list">
        {result.cases.map((item) => (
          <CaseCard key={item.name} item={item} />
        ))}
      </div>

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

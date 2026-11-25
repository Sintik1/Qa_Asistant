import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FileUploadField } from '../components/upload/FileUploadField'
import { UploadSection } from '../components/upload/UploadSection'
import { TaskNameField } from '../components/form/TaskNameField'
import { PromptField } from '../components/form/PromptField'
import { ProjectSelect } from '../components/form/ProjectSelect'
import { LibraryPanel } from '../components/management/LibraryPanel'
import { ChunkSettingsForm } from '../components/generation/ChunkSettingsForm'
import { GenerationAlerts } from '../components/generation/GenerationAlerts'
import { GenerationResults } from '../components/generation/GenerationResults'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ProgressBar } from '../components/ui/ProgressBar'
import { useFileUpload } from '../hooks/useFileUpload'
import { useTestCaseGeneration } from '../hooks/useTestCaseGeneration'
import {
  DEFAULT_PROJECT_ID,
  ERROR_MESSAGES,
} from '../utils/constants'
import { extractLibraryFile, getHealth, isApiConfigured } from '../api'
import { ApiRequestError } from '../api/errors'
import type { LibraryItem } from '../api/library'
import { combineTemplateSources, TEMPLATE_TEXT_MAX } from '../utils/templateText'
import {
  fillPromptPlaceholders,
  promptHasRequirementsMarker,
} from '../utils/fillPromptPlaceholders'
import { validateUploadFile } from '../utils/fileValidation'

/**
 * Главный экран: загрузка → API-генерация → экспорт CSV/DOCX
 * + перегенерация с параметрами чанкинга.
 */
export function HomePage() {
  const navigate = useNavigate()
  const requirements = useFileUpload()
  const templates = useFileUpload()
  const generation = useTestCaseGeneration()
  const [taskName, setTaskName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [requirementsText, setRequirementsText] = useState('')
  const [promptNote, setPromptNote] = useState<string | null>(null)
  const [selectedTemplate, setSelectedTemplate] = useState<LibraryItem | null>(null)
  const [projectId, setProjectId] = useState(DEFAULT_PROJECT_ID)
  const [formError, setFormError] = useState<string | null>(null)

  const isBusy =
    generation.status === 'extracting' || generation.status === 'generating'
  const canSubmit = Boolean(requirements.file) && !isBusy
  const showChunkControls =
    generation.showChunkPanel || generation.status === 'success'

  const buildGenerationContext = async () => {
    let fileText = ''
    if (templates.file) {
      const extracted = await extractLibraryFile(templates.file.file)
      fileText = extracted.text
    }
    const templateText = combineTemplateSources(selectedTemplate?.content ?? '', fileText)
    if (templateText.length > TEMPLATE_TEXT_MAX) {
      throw new Error(`Текст шаблона длиннее ${TEMPLATE_TEXT_MAX} символов`)
    }
    return {
      taskName,
      prompt,
      requirementsFileName: requirements.file?.name,
      ...(templateText ? { templateText } : {}),
    }
  }

  const applyRequirementsText = (nextPrompt: string, extracted: string, template = '') => {
    const filled = fillPromptPlaceholders(nextPrompt, extracted, template)
    setPrompt(filled)
    if (promptHasRequirementsMarker(nextPrompt)) {
      setPromptNote('Текст файла требований вставлен вместо «*Тут текст требований*».')
    } else if (extracted) {
      setPromptNote(
        'В промпте нет маркера «*Тут текст требований*». Выберите промпт с этим маркером, и текст файла встанет на его место.',
      )
    }
  }

  const handleRequirementsChange = async (file: File | null) => {
    requirements.setFromFile(file)
    generation.clearError()
    setFormError(null)
    setPromptNote(null)
    if (!file) {
      setRequirementsText('')
      return
    }
    if (!validateUploadFile(file).ok) {
      setRequirementsText('')
      return
    }
    try {
      const extracted = await extractLibraryFile(file)
      setRequirementsText(extracted.text)
      applyRequirementsText(prompt, extracted.text, selectedTemplate?.content ?? '')
    } catch (error) {
      setRequirementsText('')
      setFormError(errorText(error))
    }
  }

  const ensureTokenReady = async (): Promise<boolean> => {
    if (generation.apiReady) return true
    try {
      const health = await getHealth()
      if (health.ai?.configured) return true
    } catch {
      // fall through to form error
    }
    setFormError(ERROR_MESSAGES.MISSING_TOKEN)
    return false
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setFormError(null)
    generation.clearError()

    if (!requirements.file) {
      setFormError('Загрузите файл требований')
      return
    }

    if (!isApiConfigured()) {
      setFormError(
        'Не задан VITE_API_BASE_URL. Укажите URL Flask API в qa-assistant/.env.local',
      )
      return
    }

    if (!(await ensureTokenReady())) return

    try {
      await generation.generate(requirements.file, await buildGenerationContext())
    } catch (error) {
      setFormError(errorText(error))
    }
  }

  const handleRegenerate = async () => {
    if (!requirements.file || isBusy) return
    setFormError(null)
    generation.clearError()
    if (!(await ensureTokenReady())) return
    try {
      await generation.generate(requirements.file, await buildGenerationContext())
    } catch (error) {
      setFormError(errorText(error))
    }
  }

  return (
    <div>
      <PageHeader
        title="Написание тест-кейсов"
        description="Генерация тест-кейсов из документов ФД/HLD с помощью нейросети."
      />

      <form className="space-y-6" onSubmit={(e) => void handleSubmit(e)}>
        <UploadSection>
          <FileUploadField
            id="requirements-file"
            label="Файл требований (.pdf, .docx, .doc, .md)"
            selectedFile={requirements.file}
            onFileChange={handleRequirementsChange}
            error={requirements.error ?? undefined}
          />
          <FileUploadField
            id="templates-file"
            label="Шаблоны тестовых сценариев (.pdf, .docx, .doc, .md)"
            selectedFile={templates.file}
            onFileChange={templates.setFromFile}
            error={templates.error ?? undefined}
          />
          <TaskNameField value={taskName} onChange={setTaskName} />
        </UploadSection>

        <PromptField
          value={prompt}
          onChange={(value) => {
            setPrompt(value)
            setPromptNote(null)
          }}
        />
        {promptNote ? <p className="text-xs text-slate-600">{promptNote}</p> : null}

        <ProjectSelect
          value={projectId}
          options={[DEFAULT_PROJECT_ID]}
          onChange={setProjectId}
        />

        <LibraryPanel
          title="Управление промтами"
          addLabel="Добавить промт"
          kind="prompt"
          onUse={(item) =>
            applyRequirementsText(
              item.content,
              requirementsText,
              selectedTemplate?.content ?? '',
            )
          }
        />
        <LibraryPanel
          title="Управление шаблонами"
          addLabel="Добавить шаблон"
          kind="template"
          selectedId={selectedTemplate?.id}
          onUse={(item) => {
            setSelectedTemplate(item)
            setPrompt((current) =>
              fillPromptPlaceholders(current, requirementsText, item.content),
            )
          }}
          onClearSelection={() => setSelectedTemplate(null)}
          onDeleted={(id) => {
            if (selectedTemplate?.id === id) setSelectedTemplate(null)
          }}
        />
        {selectedTemplate ? (
          <p className="text-xs text-slate-600">
            Для генерации выбран шаблон: {selectedTemplate.name}
          </p>
        ) : null}

        {showChunkControls ? (
          <ChunkSettingsForm
            value={generation.chunkSettings}
            onChange={generation.setChunkSettings}
            disabled={isBusy}
          />
        ) : null}

        <GenerationAlerts
          formError={formError}
          generationError={generation.error}
          warning={generation.warning}
          onOpenSettings={() => navigate('/settings')}
          onClearGenerationError={generation.clearError}
          onClearRequirements={requirements.clear}
          onRetry={() => {
            void handleRegenerate()
          }}
          onClearWarning={generation.clearWarning}
        />

        {isBusy && generation.progressLabel ? (
          <ProgressBar label={generation.progressLabel} />
        ) : null}

        {generation.result && generation.status === 'success' ? (
          <GenerationResults
            result={generation.result}
            onDownloadCsv={generation.downloadResultCsv}
            onRegenerateClick={() => generation.setShowChunkPanel(true)}
          />
        ) : null}

        <div className="app-actions">
          <Button type="submit" disabled={!canSubmit} className="sm:min-w-56">
            Генерировать тест-кейсы
          </Button>
          {showChunkControls && requirements.file ? (
            <Button
              type="button"
              variant="secondary"
              disabled={isBusy}
              onClick={() => {
                generation.setShowChunkPanel(true)
                void handleRegenerate()
              }}
            >
              Применить и перегенерировать
            </Button>
          ) : null}
        </div>

        <p className="text-xs text-slate-500">
          Режим API: Flask ({isApiConfigured() ? 'подключён' : 'нет VITE_API_BASE_URL'}
          ). Нужны вход (Supabase Auth) и токен в{' '}
          <Link
            to="/settings"
            className="inline-flex min-h-11 items-center text-violet-700 underline"
          >
            настройках
          </Link>{' '}
          (или настроенный AI на сервере). Для .md текст читается в браузере; PDF/DOCX —
          thin-generate по метаданным до серверного extract.
        </p>
      </form>
    </div>
  )
}

function errorText(error: unknown): string {
  if (error instanceof ApiRequestError && error.message) return error.message
  if (error instanceof Error && error.message) return error.message
  return 'Не удалось прочитать шаблон'
}

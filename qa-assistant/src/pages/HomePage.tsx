import { useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { FileUploadField } from '../components/upload/FileUploadField'
import { UploadSection } from '../components/upload/UploadSection'
import { TaskNameField } from '../components/form/TaskNameField'
import { PromptField } from '../components/form/PromptField'
import { ProjectSelect } from '../components/form/ProjectSelect'
import { ManagementCard } from '../components/management/ManagementCard'
import { ChunkSettingsForm } from '../components/generation/ChunkSettingsForm'
import { GenerationAlerts } from '../components/generation/GenerationAlerts'
import { GenerationResults } from '../components/generation/GenerationResults'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ProgressBar } from '../components/ui/ProgressBar'
import { useFileUpload } from '../hooks/useFileUpload'
import { useTestCaseGeneration } from '../hooks/useTestCaseGeneration'
import {
  API_TOKEN_STORAGE_KEY,
  DEFAULT_PROJECT_ID,
  ERROR_MESSAGES,
} from '../utils/constants'

/**
 * Главный экран: загрузка (M1) → mock-генерация (M2) → экспорт CSV/DOCX (M3/S2)
 * + перегенерация с параметрами чанкинга (S1).
 */
export function HomePage() {
  const navigate = useNavigate()
  const requirements = useFileUpload()
  const templates = useFileUpload()
  const generation = useTestCaseGeneration()
  const [taskName, setTaskName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [projectId, setProjectId] = useState(DEFAULT_PROJECT_ID)
  const [formError, setFormError] = useState<string | null>(null)

  const isBusy =
    generation.status === 'extracting' || generation.status === 'generating'
  const canSubmit = Boolean(requirements.file) && !isBusy
  const showChunkControls =
    generation.showChunkPanel || generation.status === 'success'

  const generationContext = {
    taskName,
    prompt,
    requirementsFileName: requirements.file?.name,
  }

  const handleRequirementsChange = (file: File | null) => {
    requirements.setFromFile(file)
    // B4: смена файла сбрасывает stale generation.error
    generation.clearError()
    setFormError(null)
  }

  const handleSubmit = async (event: FormEvent) => {
    event.preventDefault()
    setFormError(null)
    generation.clearError()

    if (!requirements.file) {
      setFormError('Загрузите файл требований')
      return
    }

    const token = localStorage.getItem(API_TOKEN_STORAGE_KEY)?.trim()
    if (!token) {
      setFormError(ERROR_MESSAGES.MISSING_TOKEN)
      return
    }

    await generation.generate(requirements.file, generationContext)
  }

  const handleRegenerate = async () => {
    if (!requirements.file || isBusy) return
    setFormError(null)
    generation.clearError()
    await generation.generate(requirements.file, generationContext)
  }

  return (
    <div>
      <PageHeader
        title="Написание тест-кейсов"
        description="Генерация тест-кейсов из документов ФД/HLD с помощью нейросети."
      />

      <form className="space-y-6" onSubmit={handleSubmit}>
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

        <PromptField value={prompt} onChange={setPrompt} />

        <ProjectSelect
          value={projectId}
          options={[DEFAULT_PROJECT_ID]}
          onChange={setProjectId}
        />

        <ManagementCard title="Управление промтами" addLabel="Добавить промт" />
        <ManagementCard
          title="Управление шаблонами"
          addLabel="Добавить шаблон"
        />

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
          Mock-режим: API не вызывается. Имена файлов для проверки:{' '}
          <code>empty</code>/<code>noreq</code> (нет требований),{' '}
          <code>fail</code> (ошибка API), <code>slow</code>/<code>notify</code>{' '}
          (уведомление &gt;30с). Токен:{' '}
          <Link
            to="/settings"
            className="inline-flex min-h-11 items-center text-violet-700 underline"
          >
            настройки
          </Link>
          .
        </p>
      </form>
    </div>
  )
}

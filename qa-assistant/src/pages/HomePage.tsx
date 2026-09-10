import { useState, type FormEvent } from 'react'
import { FileUploadField } from '../components/upload/FileUploadField'
import { UploadSection } from '../components/upload/UploadSection'
import { TaskNameField } from '../components/form/TaskNameField'
import { PromptField } from '../components/form/PromptField'
import { ProjectSelect } from '../components/form/ProjectSelect'
import { ManagementCard } from '../components/management/ManagementCard'
import { Button } from '../components/ui/Button'
import { PageHeader } from '../components/ui/PageHeader'
import { ProgressBar } from '../components/ui/ProgressBar'
import { ErrorMessage } from '../components/ui/ErrorMessage'
import { useFileUpload } from '../hooks/useFileUpload'
import { DEFAULT_PROJECT_ID } from '../utils/constants'

/**
 * Main screen from Figma: «Написание тест-кейсов».
 * Structure only — generation API wiring comes later.
 */
export function HomePage() {
  const requirements = useFileUpload()
  const templates = useFileUpload()
  const [taskName, setTaskName] = useState('')
  const [prompt, setPrompt] = useState('')
  const [projectId, setProjectId] = useState(DEFAULT_PROJECT_ID)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const canSubmit = Boolean(requirements.file) && !isSubmitting

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault()
    if (!requirements.file) {
      setFormError('Загрузите файл требований')
      return
    }
    setFormError(null)
    // Placeholder: backend integration is out of scope for structure step
    setIsSubmitting(true)
    window.setTimeout(() => setIsSubmitting(false), 600)
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
            label="Файл требований (.docx)"
            selectedFile={requirements.file}
            onFileChange={requirements.setFromFile}
            error={requirements.error ?? undefined}
          />
          <FileUploadField
            id="templates-file"
            label="Шаблоны тестовых сценариев (.docx)"
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

        {formError ? <ErrorMessage message={formError} /> : null}

        {isSubmitting ? (
          <ProgressBar label="Генерация тест-кейсов..." />
        ) : null}

        <Button type="submit" disabled={!canSubmit}>
          Отправить на обработку нейросетью
        </Button>
      </form>
    </div>
  )
}

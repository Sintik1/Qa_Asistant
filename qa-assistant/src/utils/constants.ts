import type { AllowedFileExtension } from '../types'

/** Max upload size from TZ: 100 MB */
export const MAX_FILE_SIZE_BYTES = 100 * 1024 * 1024

export const ALLOWED_EXTENSIONS: readonly AllowedFileExtension[] = [
  '.pdf',
  '.docx',
  '.doc',
  '.md',
] as const

export const ACCEPT_FILE_TYPES = ALLOWED_EXTENSIONS.join(',')

export const ERROR_MESSAGES = {
  INVALID_FORMAT:
    'Поддерживаются только PDF, DOCX, DOC и Markdown-файлы',
  FILE_TOO_LARGE: 'Размер файла превышает допустимый лимит (100 МБ)',
  EMPTY_FILE: 'Файл не содержит текста. Проверьте его содержимое.',
  CORRUPT_FILE:
    'Не удалось извлечь текст из файла. Проверьте его целостность.',
  NO_REQUIREMENTS:
    'В документе не обнаружено требований. Проверьте файл.',
  API_UNAVAILABLE:
    'Не удалось подключиться к сервису анализа. Проверьте подключение или повторите попытку.',
  API_EMPTY:
    'Сервис анализа не сгенерировал тест-кейсы. Повторите попытку.',
  API_503:
    'Сервис анализа временно недоступен. Повторите через 5 минут.',
  API_429: 'Превышен лимит запросов к API. Подождите 1 час.',
  INVALID_TOKEN: 'Токен недействителен. Обновите его в настройках.',
  MISSING_TOKEN: 'Не настроен API-токен. Перейдите в настройки.',
  INVALID_CSV:
    'Сервис вернул некорректный результат. Свяжитесь с администратором.',
} as const

export const DEFAULT_PROJECT_ID = 'default'

export const APP_TITLE = 'QA Assistant'
export const APP_SUBTITLE = 'Помощник для QA-инженера'

export { isApiConfigured, apiJson } from './client'
export {
  ApiRequestError,
  messageForApiError,
  resolveApiError,
} from './errors'
export type { ApiErrorAction } from './errors'
export { createDocument, listDocuments, uploadDocument } from './documents'
export type { UploadDocumentResult } from './documents'
export {
  createRun,
  listRuns,
  listTestCases,
  generateRun,
  chunkSettingsToApi,
} from './runs'
export { getSettings, patchSettings, getHealth, settingsToChunk } from './settings'
export { chatRequirements } from './chat'
export type { ChatCitation, ChatResponse } from './chat'
export type {
  ApiDocument,
  ApiRun,
  ApiTestCase,
  ApiUserSettings,
  ApiHealth,
  GenerateResponse,
} from './types'

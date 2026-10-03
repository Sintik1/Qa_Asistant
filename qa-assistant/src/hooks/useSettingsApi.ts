import { useCallback, useEffect, useState } from 'react'
import {
  getSettings,
  isApiConfigured,
  messageForApiError,
  patchSettings,
  settingsToChunk,
} from '../api'
import type { ChunkSettings } from '../types'
import { DEFAULT_CHUNK_SETTINGS } from '../utils/chunkSettings'

interface UseSettingsApiResult {
  chunkSettings: ChunkSettings
  hasApiToken: boolean
  loading: boolean
  error: string | null
  saveChunkSettings: (next: ChunkSettings) => Promise<void>
  setHasApiToken: (value: boolean) => Promise<void>
  reload: () => Promise<void>
}

export function useSettingsApi(): UseSettingsApiResult {
  const [chunkSettings, setChunkSettings] = useState<ChunkSettings>(
    DEFAULT_CHUNK_SETTINGS,
  )
  const [hasApiToken, setHasApiTokenState] = useState(false)
  const [loading, setLoading] = useState(isApiConfigured())
  const [error, setError] = useState<string | null>(null)

  const reload = useCallback(async () => {
    if (!isApiConfigured()) {
      setLoading(false)
      return
    }
    setLoading(true)
    setError(null)
    try {
      const settings = await getSettings()
      setChunkSettings(settingsToChunk(settings))
      setHasApiTokenState(settings.has_api_token)
    } catch (err) {
      setError(messageForApiError(err))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void reload()
  }, [reload])

  const saveChunkSettings = useCallback(async (next: ChunkSettings) => {
    setChunkSettings(next)
    if (!isApiConfigured()) return
    try {
      const saved = await patchSettings({
        chunk_size: next.chunkSize,
        chunk_overlap: next.chunkOverlap,
        chunk_method: next.chunkMethod,
      })
      setChunkSettings(settingsToChunk(saved))
      setError(null)
    } catch (err) {
      setError(messageForApiError(err))
      throw err
    }
  }, [])

  const setHasApiToken = useCallback(async (value: boolean) => {
    setHasApiTokenState(value)
    if (!isApiConfigured()) return
    try {
      const saved = await patchSettings({ has_api_token: value })
      setHasApiTokenState(saved.has_api_token)
      setError(null)
    } catch (err) {
      setError(messageForApiError(err))
      throw err
    }
  }, [])

  return {
    chunkSettings,
    hasApiToken,
    loading,
    error,
    saveChunkSettings,
    setHasApiToken,
    reload,
  }
}

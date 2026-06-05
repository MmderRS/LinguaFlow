import { defineStore } from 'pinia'

import { fetchSettings, updateAsrProvider, updateTranslationProvider } from '../services/api'
import type { PublicSettings } from '../types'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: null as PublicSettings | null,
    loading: false,
    error: '',
  }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        this.settings = await fetchSettings()
      } catch (error) {
        this.error = error instanceof Error ? error.message : '加载设置失败'
      } finally {
        this.loading = false
      }
    },
    async setAsrProvider(provider: string) {
      this.settings = await updateAsrProvider(provider)
    },
    async setTranslationProvider(provider: string) {
      this.settings = await updateTranslationProvider(provider)
    },
  },
})

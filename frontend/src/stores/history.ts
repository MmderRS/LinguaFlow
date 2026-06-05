import { defineStore } from 'pinia'

import {
  deleteHistoryRecord,
  deleteHistorySession,
  fetchHistory,
} from '../services/api'
import type { HistoryItem } from '../types'

export const useHistoryStore = defineStore('history', {
  state: () => ({
    items: [] as HistoryItem[],
    total: 0,
    page: 1,
    pageSize: 20,
    query: '',
    sessionId: '',
    loading: false,
    error: '',
  }),
  actions: {
    async load() {
      this.loading = true
      this.error = ''
      try {
        const page = await fetchHistory({
          query: this.query || undefined,
          sessionId: this.sessionId || undefined,
          page: this.page,
          pageSize: this.pageSize,
        })
        this.items = page.items
        this.total = page.total
      } catch (error) {
        this.error = error instanceof Error ? error.message : '加载历史失败'
      } finally {
        this.loading = false
      }
    },
    async removeRecord(recordId: number) {
      await deleteHistoryRecord(recordId)
      await this.load()
    },
    async removeSession(sessionId: string) {
      await deleteHistorySession(sessionId)
      await this.load()
    },
    prepend(item: HistoryItem) {
      this.items = [item, ...this.items]
      this.total += 1
    },
    replaceBySegment(sessionId: string, segmentId: string, sourceText: string, targetText: string) {
      this.items = this.items.map((item) => {
        if (item.session_id === sessionId && item.segment_id === segmentId) {
          return {
            ...item,
            source_text: sourceText,
            target_text: targetText,
            corrected: true,
          }
        }
        return item
      })
    },
  },
})

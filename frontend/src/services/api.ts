import type { HistoryPage, PublicSettings, TermItem } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers || {}),
    },
    ...init,
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed: ${response.status}`)
  }

  if (response.status === 204) {
    return undefined as T
  }

  return response.json() as Promise<T>
}

export function getApiBase() {
  return API_BASE
}

export function fetchSettings() {
  return request<PublicSettings>('/api/settings')
}

export function fetchTerms(query = '') {
  const search = query ? `?query=${encodeURIComponent(query)}` : ''
  return request<TermItem[]>(`/api/terms${search}`)
}

export function createTerm(payload: { domain: string; source: string; target: string }) {
  return request<TermItem>('/api/terms', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateTerm(termId: number, payload: { domain?: string; target?: string }) {
  return request<TermItem>(`/api/terms/${termId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function deleteTerm(termId: number) {
  return request<{ deleted: number }>(`/api/terms/${termId}`, {
    method: 'DELETE',
  })
}

export function fetchHistory(params: { query?: string; sessionId?: string; page?: number; pageSize?: number }) {
  const search = new URLSearchParams()
  if (params.query) search.set('query', params.query)
  if (params.sessionId) search.set('session_id', params.sessionId)
  if (params.page) search.set('page', String(params.page))
  if (params.pageSize) search.set('page_size', String(params.pageSize))
  return request<HistoryPage>(`/api/history?${search.toString()}`)
}

export function deleteHistoryRecord(recordId: number) {
  return request<{ deleted: number }>(`/api/history/${recordId}`, { method: 'DELETE' })
}

export function deleteHistorySession(sessionId: string) {
  return request<{ deleted: number }>(`/api/history/session/${encodeURIComponent(sessionId)}`, {
    method: 'DELETE',
  })
}

export function exportHistoryUrl(params: { query?: string; sessionId?: string }) {
  const search = new URLSearchParams()
  if (params.query) search.set('query', params.query)
  if (params.sessionId) search.set('session_id', params.sessionId)
  return `${API_BASE}/api/history/export?${search.toString()}`
}

export function applyManualCorrection(
  sessionId: string,
  segmentId: string,
  payload: { source_text?: string; target_text?: string },
) {
  return request(`/api/history/session/${encodeURIComponent(sessionId)}/segment/${encodeURIComponent(segmentId)}/correction`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

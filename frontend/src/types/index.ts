export type ConnectionState = 'disconnected' | 'connected' | 'listening' | 'idle' | 'heartbeat'

export interface TermItem {
  id: number
  domain: string
  source: string
  target: string
  builtin: boolean
  created_at?: string | null
}

export interface HistoryItem {
  id: number
  session_id: string
  segment_id: string
  source_text: string
  target_text: string
  corrected: boolean
  created_at?: string | null
  updated_at?: string | null
}

export interface HistoryPage {
  total: number
  page: number
  page_size: number
  items: HistoryItem[]
}

export interface PublicSettings {
  asr_provider: string
  translation_provider: string
  available_asr_providers: string[]
  available_translation_providers: string[]
  websocket_path: string
  supports_manual_correction: boolean
  supports_mock_input: boolean
}

export interface SubtitleSegment {
  segmentId: string
  source: string
  target: string
  corrected: boolean
  isFinal: boolean
  recordId?: number | null
  terms?: Array<Record<string, unknown>>
}

export interface StatusMessage {
  type: 'status'
  session_id: string
  state: ConnectionState | string
  detail: string
}

export interface ASRMessage {
  type: 'asr'
  segment_id: string
  text: string
  is_final: boolean
}

export interface TranslationMessage {
  type: 'translation'
  segment_id: string
  source: string
  target: string
  is_final: boolean
  terms: Array<Record<string, unknown>>
  record_id?: number | null
  corrected: boolean
}

export interface CorrectionMessage {
  type: 'correction'
  segment_id: string
  source: string
  target: string
  record_id?: number | null
  corrected: boolean
}

export interface ErrorMessage {
  type: 'error'
  detail: string
}

export type RealtimeServerMessage =
  | StatusMessage
  | ASRMessage
  | TranslationMessage
  | CorrectionMessage
  | ErrorMessage

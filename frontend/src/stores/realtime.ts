import { defineStore } from 'pinia'

import { applyManualCorrection } from '../services/api'
import { RealtimeSocketClient } from '../services/ws'
import type {
  ASRMessage,
  CorrectionMessage,
  ErrorMessage,
  RealtimeServerMessage,
  StatusMessage,
  SubtitleSegment,
  TranslationMessage,
} from '../types'

const createSessionId = () => `session-${Math.random().toString(36).slice(2, 10)}`

export const useRealtimeStore = defineStore('realtime', {
  state: () => ({
    client: null as RealtimeSocketClient | null,
    sessionId: createSessionId(),
    connectionState: 'disconnected',
    connectionDetail: '尚未连接',
    partialText: '',
    segments: [] as SubtitleSegment[],
    debugInput: '',
    recording: false,
    error: '',
    mediaRecorder: null as MediaRecorder | null,
    websocketPath: '/ws/realtime',
  }),
  getters: {
    latestSegments: (state) => [...state.segments].reverse(),
  },
  actions: {
    async connect(path = '/ws/realtime') {
      this.websocketPath = path
      this.error = ''
      this.client?.close()
      this.client = new RealtimeSocketClient()
      const socket = this.client.connect(path, (message) => this.handleMessage(message))
      socket.onopen = () => {
        this.connectionState = 'connected'
        this.connectionDetail = '实时链路已建立'
        this.client?.sendJson({
          type: 'start',
          session_id: this.sessionId,
          mime_type: 'audio/webm',
        })
      }
      socket.onclose = () => {
        this.connectionState = 'disconnected'
        this.connectionDetail = '实时链路已断开'
        this.recording = false
      }
      socket.onerror = () => {
        this.error = 'WebSocket 连接异常'
      }
    },
    disconnect() {
      this.client?.close()
      this.recording = false
      this.mediaRecorder?.stop()
      this.mediaRecorder = null
    },
    handleMessage(message: RealtimeServerMessage) {
      if (message.type === 'status') {
        this.applyStatus(message)
        return
      }
      if (message.type === 'asr') {
        this.applyAsr(message)
        return
      }
      if (message.type === 'translation') {
        this.applyTranslation(message)
        return
      }
      if (message.type === 'correction') {
        this.applyCorrection(message)
        return
      }
      if (message.type === 'error') {
        this.applyError(message)
      }
    },
    applyStatus(message: StatusMessage) {
      this.connectionState = message.state
      this.connectionDetail = message.detail || message.state
      if (message.session_id) {
        this.sessionId = message.session_id
      }
    },
    applyAsr(message: ASRMessage) {
      if (message.is_final) {
        const existing = this.segments.find((item) => item.segmentId === message.segment_id)
        if (existing) {
          existing.source = message.text
          existing.isFinal = true
        } else {
          this.segments.push({
            segmentId: message.segment_id,
            source: message.text,
            target: '',
            corrected: false,
            isFinal: true,
          })
        }
        this.partialText = ''
        return
      }
      this.partialText = message.text
    },
    applyTranslation(message: TranslationMessage) {
      const existing = this.segments.find((item) => item.segmentId === message.segment_id)
      if (existing) {
        existing.source = message.source
        existing.target = message.target
        existing.corrected = message.corrected
        existing.isFinal = message.is_final
        existing.recordId = message.record_id
        existing.terms = message.terms
      } else {
        this.segments.push({
          segmentId: message.segment_id,
          source: message.source,
          target: message.target,
          corrected: message.corrected,
          isFinal: message.is_final,
          recordId: message.record_id,
          terms: message.terms,
        })
      }
    },
    applyCorrection(message: CorrectionMessage) {
      const existing = this.segments.find((item) => item.segmentId === message.segment_id)
      if (!existing) {
        this.segments.push({
          segmentId: message.segment_id,
          source: message.source,
          target: message.target,
          corrected: true,
          isFinal: true,
          recordId: message.record_id,
        })
        return
      }
      existing.source = message.source
      existing.target = message.target
      existing.corrected = true
      existing.recordId = message.record_id
    },
    applyError(message: ErrorMessage) {
      this.error = message.detail
    },
    async sendDebugText(text: string) {
      if (!text.trim()) return
      if (!this.client) {
        await this.connect(this.websocketPath)
      }
      this.client?.sendJson({ type: 'debug_text', text })
      this.debugInput = ''
    },
    async startRecording() {
      if (!navigator.mediaDevices?.getUserMedia) {
        this.error = '当前浏览器不支持录音'
        return
      }
      if (!this.client) {
        await this.connect(this.websocketPath)
      }
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' })
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.client?.sendBytes(event.data)
        }
      }
      recorder.onstop = () => {
        this.client?.sendJson({ type: 'stop' })
        stream.getTracks().forEach((track) => track.stop())
      }
      recorder.start(900)
      this.mediaRecorder = recorder
      this.recording = true
    },
    stopRecording() {
      this.mediaRecorder?.stop()
      this.mediaRecorder = null
      this.recording = false
    },
    async saveManualCorrection(segmentId: string, payload: { sourceText?: string; targetText?: string }) {
      await applyManualCorrection(this.sessionId, segmentId, {
        source_text: payload.sourceText,
        target_text: payload.targetText,
      })
    },
    resetSession() {
      this.sessionId = createSessionId()
      this.partialText = ''
      this.segments = []
      this.error = ''
      this.connectionDetail = '会话已重置'
      this.client?.sendJson({
        type: 'start',
        session_id: this.sessionId,
        mime_type: 'audio/webm',
      })
    },
  },
})

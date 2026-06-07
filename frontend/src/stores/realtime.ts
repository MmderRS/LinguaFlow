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
const SILENCE_CHECK_MS = 120
const SILENCE_END_MS = 700
const MIN_SEGMENT_MS = 700
const MAX_SEGMENT_MS = 10000
const SPEECH_RMS_THRESHOLD = 0.035

function pickRecordingMimeType(): string {
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
  ]

  for (const candidate of candidates) {
    if (typeof MediaRecorder !== 'undefined' && MediaRecorder.isTypeSupported(candidate)) {
      return candidate
    }
  }

  return ''
}

function nowMs() {
  return typeof performance !== 'undefined' ? performance.now() : Date.now()
}

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
    mediaStream: null as MediaStream | null,
    audioContext: null as AudioContext | null,
    analyser: null as AnalyserNode | null,
    analyserData: null as Uint8Array<ArrayBuffer> | null,
    silenceTimer: 0,
    segmentTimer: 0,
    segmentStartedAt: 0,
    speechStartedAt: 0,
    lastVoiceAt: 0,
    hasVoiceInSegment: false,
    restartingSegment: false,
    websocketPath: '/ws/realtime',
    asrProvider: '',
    translationProvider: '',
    isMockAsr: false,
  }),
  getters: {
    latestSegments: (state) => [...state.segments].reverse(),
    hasRealAsr: (state) => !state.isMockAsr,
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
          mime_type: pickRecordingMimeType() || 'audio/webm',
        })
      }
      socket.onclose = () => {
        this.connectionState = 'disconnected'
        this.connectionDetail = '实时链路已断开'
        this.recording = false
        this.cleanupRecorder()
      }
      socket.onerror = () => {
        this.error = 'WebSocket 连接异常'
      }
    },
    disconnect() {
      this.client?.close()
      this.cleanupRecorder()
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
      if (message.asr_provider) {
        this.asrProvider = message.asr_provider
      }
      if (message.translation_provider) {
        this.translationProvider = message.translation_provider
      }
      this.isMockAsr = Boolean(message.is_mock_asr)
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
      await this.client?.waitUntilOpen()
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
      await this.client?.waitUntilOpen()
      this.cleanupRecorder()
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true })
      this.recording = true
      this.connectionDetail = this.isMockAsr
        ? '演示录音已开始'
        : '实时识别中：检测到一句话结束后自动提交'
      this.startRecorderSegment()
      if (!this.isMockAsr) {
        await this.startVoiceActivityDetection()
      }
    },
    stopRecording() {
      this.recording = false
      this.restartingSegment = false
      this.stopVoiceActivityDetection()
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop()
      } else {
        this.client?.sendJson({ type: 'stop' })
      }
      this.mediaRecorder = null
      this.mediaStream?.getTracks().forEach((track) => track.stop())
      this.mediaStream = null
    },
    startRecorderSegment() {
      if (!this.mediaStream) return
      const mimeType = pickRecordingMimeType()
      const recorder = mimeType
        ? new MediaRecorder(this.mediaStream, { mimeType })
        : new MediaRecorder(this.mediaStream)

      this.segmentStartedAt = nowMs()
      this.speechStartedAt = 0
      this.lastVoiceAt = 0
      this.hasVoiceInSegment = false

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.client?.sendBytes(event.data)
        }
      }
      recorder.onstop = () => {
        const shouldFinalize = this.hasVoiceInSegment || this.restartingSegment
        this.client?.sendJson({ type: shouldFinalize ? 'finalize_audio' : 'stop' })
        if (this.recording && !this.isMockAsr) {
          this.startRecorderSegment()
        }
        this.restartingSegment = false
      }
      if (this.isMockAsr) {
        recorder.start(900)
      } else {
        recorder.start()
      }
      this.mediaRecorder = recorder
    },
    async startVoiceActivityDetection() {
      if (!this.mediaStream) return
      this.audioContext = new AudioContext()
      const source = this.audioContext.createMediaStreamSource(this.mediaStream)
      this.analyser = this.audioContext.createAnalyser()
      this.analyser.fftSize = 1024
      source.connect(this.analyser)
      this.analyserData = new Uint8Array(new ArrayBuffer(this.analyser.fftSize))
      this.silenceTimer = window.setInterval(() => {
        this.checkVoiceActivity()
      }, SILENCE_CHECK_MS)
    },
    checkVoiceActivity() {
      if (!this.recording || !this.analyser || !this.analyserData || this.isMockAsr) return
      this.analyser.getByteTimeDomainData(this.analyserData)

      let sum = 0
      for (const value of this.analyserData) {
        const normalized = (value - 128) / 128
        sum += normalized * normalized
      }
      const rms = Math.sqrt(sum / this.analyserData.length)
      const now = nowMs()

      if (rms >= SPEECH_RMS_THRESHOLD) {
        this.hasVoiceInSegment = true
        if (!this.speechStartedAt) {
          this.speechStartedAt = now
        }
        this.lastVoiceAt = now
        return
      }

      if (!this.hasVoiceInSegment || !this.lastVoiceAt) return
      const speechDuration = now - this.speechStartedAt
      const silenceDuration = now - this.lastVoiceAt
      const segmentDuration = now - this.segmentStartedAt
      const reachedNaturalPause = speechDuration >= MIN_SEGMENT_MS && silenceDuration >= SILENCE_END_MS
      const reachedMaxDuration = segmentDuration >= MAX_SEGMENT_MS

      if (reachedNaturalPause || reachedMaxDuration) {
        this.finalizeCurrentAudioSegment()
      }
    },
    finalizeCurrentAudioSegment() {
      if (!this.recording || !this.mediaRecorder || this.mediaRecorder.state === 'inactive') return
      this.restartingSegment = true
      this.mediaRecorder.stop()
    },
    stopVoiceActivityDetection() {
      window.clearInterval(this.silenceTimer)
      this.silenceTimer = 0
      void this.audioContext?.close()
      this.audioContext = null
      this.analyser = null
      this.analyserData = null
    },
    cleanupRecorder() {
      window.clearInterval(this.segmentTimer)
      this.segmentTimer = 0
      this.stopVoiceActivityDetection()
      this.recording = false
      this.restartingSegment = false
      if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
        this.mediaRecorder.stop()
      }
      this.mediaRecorder = null
      this.mediaStream?.getTracks().forEach((track) => track.stop())
      this.mediaStream = null
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
        mime_type: pickRecordingMimeType() || 'audio/webm',
      })
    },
  },
})

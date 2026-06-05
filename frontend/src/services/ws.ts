import type { RealtimeServerMessage } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function toWsBase(url: string) {
  if (url.startsWith('https://')) return url.replace('https://', 'wss://')
  if (url.startsWith('http://')) return url.replace('http://', 'ws://')
  return url
}

export class RealtimeSocketClient {
  private socket: WebSocket | null = null

  connect(path: string, onMessage: (message: RealtimeServerMessage) => void) {
    const wsUrl = `${toWsBase(API_BASE)}${path}`
    this.socket = new WebSocket(wsUrl)
    this.socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as RealtimeServerMessage
      onMessage(payload)
    }
    return this.socket
  }

  sendJson(payload: Record<string, unknown>) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(JSON.stringify(payload))
    }
  }

  sendBytes(payload: Blob) {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(payload)
    }
  }

  close() {
    this.socket?.close()
    this.socket = null
  }
}

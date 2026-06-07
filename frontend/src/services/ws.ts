import type { RealtimeServerMessage } from '../types'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

function toWsBase(url: string) {
  if (url.startsWith('https://')) return url.replace('https://', 'wss://')
  if (url.startsWith('http://')) return url.replace('http://', 'ws://')
  return url
}

export class RealtimeSocketClient {
  private socket: WebSocket | null = null
  private readyPromise: Promise<void> | null = null

  connect(path: string, onMessage: (message: RealtimeServerMessage) => void) {
    const wsUrl = `${toWsBase(API_BASE)}${path}`
    this.socket = new WebSocket(wsUrl)
    this.readyPromise = new Promise((resolve, reject) => {
      this.socket?.addEventListener('open', () => resolve(), { once: true })
      this.socket?.addEventListener('error', () => reject(new Error('WebSocket 连接失败')), { once: true })
    })
    this.socket.onmessage = (event) => {
      const payload = JSON.parse(event.data) as RealtimeServerMessage
      onMessage(payload)
    }
    return this.socket
  }

  async waitUntilOpen(timeoutMs = 5000) {
    if (this.socket?.readyState === WebSocket.OPEN) return
    if (!this.readyPromise) throw new Error('WebSocket 尚未初始化')

    await Promise.race([
      this.readyPromise,
      new Promise((_, reject) => {
        window.setTimeout(() => reject(new Error('WebSocket 连接超时')), timeoutMs)
      }),
    ])
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
    this.readyPromise = null
  }
}

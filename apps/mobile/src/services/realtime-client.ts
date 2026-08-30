import { useMobileStore } from "../stores/mobile-store"

export class RealtimeClient {
  private ws: WebSocket | null = null
  private baseUrl: string
  private deviceId: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectTimer: any = null
  private pingTimer: any = null

  constructor(serverEndpoint: string, deviceId: string) {
    this.baseUrl = serverEndpoint.replace(/^http/, "ws")
    this.deviceId = deviceId
  }

  connect() {
    if (this.ws) return

    const url = `${this.baseUrl}/api/remote/ws?device_id=${encodeURIComponent(this.deviceId)}`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      useMobileStore.getState().setConnectivity("ONLINE")
      this.startHeartbeat()
    }

    this.ws.onmessage = (event) => {
      if (event.data === "pong") return
      try {
        const payload = JSON.parse(event.data)
        this.handleEvent(payload)
      } catch {}
    }

    this.ws.onclose = () => {
      this.stopHeartbeat()
      this.ws = null
      useMobileStore.getState().setConnectivity("OFFLINE")
      this.scheduleReconnect()
    }

    this.ws.onerror = () => {
      if (this.ws) this.ws.close()
    }
  }

  private startHeartbeat() {
    this.pingTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send("ping")
      }
    }, 15000)
  }

  private stopHeartbeat() {
    if (this.pingTimer) clearInterval(this.pingTimer)
  }

  private scheduleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 15000)
      this.reconnectTimer = setTimeout(() => this.connect(), delay)
    }
  }

  private handleEvent(event: { type: string; data: any }) {
    const store = useMobileStore.getState()
    
    // Atualização em tempo real sem refresh
    if (event.type === "TASK_CREATED" || event.type === "TASK_COMPLETED") {
      // Atualiza contagens ou lista
      if (store.dashboard) {
        store.setDashboard({
          ...store.dashboard,
          tasksCount: event.type === "TASK_CREATED" ? store.dashboard.tasksCount + 1 : Math.max(0, store.dashboard.tasksCount - 1)
        })
      }
    } else if (event.type === "SYNC_COMPLETED") {
      // Limpa filas locais
    }
  }

  disconnect() {
    this.stopHeartbeat()
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }
}

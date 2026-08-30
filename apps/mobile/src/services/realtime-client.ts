import { useMobileStore } from "../stores/mobile-store"

export class RealtimeClient {
  private ws: WebSocket | null = null
  private baseUrl: string
  private deviceId: string
  private reconnectAttempts = 0
  private maxReconnectAttempts = 10
  private reconnectTimer: any = null
  private pingTimer: any = null

  constructor(serverEndpoint: string, deviceId: string) {
    this.baseUrl = serverEndpoint.replace(/^http/, "ws")
    this.deviceId = deviceId
  }

  connect() {
    if (this.ws) return

    const url = this.baseUrl + "/api/remote/ws?device_id=" + encodeURIComponent(this.deviceId)
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      this.reconnectAttempts = 0
      useMobileStore.getState().setConnectivity("ONLINE")
      this.startHeartbeat()
      this.fetchInitialState()
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

  private async fetchInitialState() {
    const store = useMobileStore.getState()
    try {
      const res = await fetch(store.serverEndpoint + "/api/realtime/state")
      if (res.ok) {
        const state = await res.json()
        if (state.active_session) {
          store.setLiveSession(state.active_session)
        }
        if (state.latest_event_sequence) {
          store.setLastEventSequence(state.latest_event_sequence)
        }
      }
    } catch {}
  }

  private startHeartbeat() {
    this.pingTimer = setInterval(async () => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send("ping")
        
        // Envia heartbeat de presença
        const store = useMobileStore.getState()
        try {
          await fetch(store.serverEndpoint + "/api/realtime/presence/heartbeat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              device_id: this.deviceId,
              device_name: store.deviceInfo.deviceName,
              platform: store.deviceInfo.platform,
              app_version: store.deviceInfo.appVersion,
              sync_status: store.offlineQueue.length > 0 ? "SYNCING" : "SYNCED"
            })
          })
        } catch {}
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
    
    if (event.type === "LIVE_STATE_UPDATED") {
      const data = event.data
      store.setLiveSession({
        session_id: data.session_id,
        device_id: data.origin_device_id || "DESKTOP-MAIN",
        origin_device_id: data.origin_device_id || "DESKTOP-MAIN",
        user_id: "user_default",
        type: data.type,
        status: data.status,
        duration_seconds: data.duration_seconds,
        remaining_seconds: data.remaining_seconds,
        current_block_id: data.current_block_id,
        version: data.version
      })
    } else if (event.type === "TASK_CREATED" || event.type === "TASK_COMPLETED") {
      if (store.dashboard) {
        store.setDashboard({
          ...store.dashboard,
          tasksCount: event.type === "TASK_CREATED" ? store.dashboard.tasksCount + 1 : Math.max(0, store.dashboard.tasksCount - 1)
        })
      }
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

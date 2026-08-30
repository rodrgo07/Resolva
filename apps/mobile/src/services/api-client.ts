import { PairingPayload, SyncOperationItem, RemoteCommandPayload } from "../types"

export class MobileApiClient {
  private baseUrl: string
  private token: string | null = null

  constructor(baseUrl: string, token: string | null = null) {
    this.baseUrl = baseUrl.replace(/\/$/, "")
    this.token = token
  }

  setToken(token: string | null) {
    this.token = token
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json"
    }
    if (this.token) {
      headers["Authorization"] = `Bearer ${this.token}`
    }
    return headers
  }

  async completePairing(payload: PairingPayload) {
    const res = await fetch(`${this.baseUrl}/api/devices/pair/complete`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify(payload)
    })
    if (!res.ok) throw new Error(`Falha no pareamento: ${res.statusText}`)
    return res.json()
  }

  async getDesktopStatus() {
    const res = await fetch(`${this.baseUrl}/api/remote/desktop/status`, { headers: this.getHeaders() })
    if (!res.ok) throw new Error("Erro ao obter status do desktop")
    return res.json()
  }

  async executeRemoteCommand(deviceId: string, command: RemoteCommandPayload) {
    const res = await fetch(`${this.baseUrl}/api/remote/commands`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        request_id: `req_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        device_id: deviceId,
        command_type: command.command_type,
        parameters: command.parameters || {}
      })
    })
    if (!res.ok) throw new Error("Falha ao executar comando remoto")
    return res.json()
  }

  async confirmRemoteAction(deviceId: string, actionId: string, confirmed: boolean) {
    const res = await fetch(`${this.baseUrl}/api/remote/actions/confirm`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({
        device_id: deviceId,
        action_id: actionId,
        confirmed
      })
    })
    if (!res.ok) throw new Error("Erro ao confirmar ação remota")
    return res.json()
  }

  async getPendingActions(deviceId: string) {
    const res = await fetch(`${this.baseUrl}/api/remote/actions/pending?device_id=${encodeURIComponent(deviceId)}`, {
      headers: this.getHeaders()
    })
    if (!res.ok) throw new Error("Erro ao buscar ações pendentes")
    return res.json()
  }

  async registerPushToken(deviceId: string, pushToken: string, platform: "ANDROID" | "IOS" = "ANDROID") {
    const res = await fetch(`${this.baseUrl}/api/remote/devices/${encodeURIComponent(deviceId)}/push-token`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ platform, push_token: pushToken })
    })
    if (!res.ok) throw new Error("Erro ao registrar push token")
    return res.json()
  }

  async pushSync(deviceId: string, operations: SyncOperationItem[]) {
    const res = await fetch(`${this.baseUrl}/api/sync/push`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ device_id: deviceId, operations })
    })
    if (!res.ok) throw new Error("Erro ao enviar sincronização push")
    return res.json()
  }

  async pullSync(deviceId: string, sinceCursor?: string) {
    const res = await fetch(`${this.baseUrl}/api/sync/pull`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ device_id: deviceId, since_cursor: sinceCursor, limit: 50 })
    })
    if (!res.ok) throw new Error("Erro ao puxar sincronização pull")
    return res.json()
  }

  async askAgent(message: string, conversationId?: number) {
    const res = await fetch(`${this.baseUrl}/api/ai/chat`, {
      method: "POST",
      headers: this.getHeaders(),
      body: JSON.stringify({ message, conversation_id: conversationId })
    })
    if (!res.ok) throw new Error("Erro ao comunicar com o Resolva Agent")
    return res.json()
  }
}

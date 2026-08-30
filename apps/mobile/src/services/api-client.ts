import { PairingPayload, SyncOperationItem } from "../types"

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
    if (!res.ok) {
      throw new Error(`Falha no pareamento: ${res.statusText}`)
    }
    return res.json()
  }

  async getBootstrap(deviceId?: string) {
    const url = deviceId 
      ? `${this.baseUrl}/api/mobile/bootstrap?device_id=${encodeURIComponent(deviceId)}`
      : `${this.baseUrl}/api/mobile/bootstrap`
    const res = await fetch(url, { headers: this.getHeaders() })
    if (!res.ok) throw new Error("Erro ao obter bootstrap")
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

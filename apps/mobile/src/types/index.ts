export type ConnectivityState = "ONLINE" | "OFFLINE" | "CONNECTING" | "SYNCING" | "ERROR" | "AUTH_REQUIRED"

export interface DeviceInfo {
  deviceId: string
  deviceName: string
  platform: "ANDROID" | "IOS"
  appVersion: string
  isPaired: boolean
  lastSyncedAt?: string
}

export interface PairingPayload {
  pairingCode?: string
  qrPayload?: string
  nonce: string
  deviceName: string
  platform: "ANDROID" | "IOS"
  appVersion: string
  deviceId?: string
}

export interface SyncOperationItem {
  operation_id: string
  device_id: string
  entity_type: string
  entity_id: string
  operation: string
  payload: Record<string, any>
  version: number
  created_at?: string
  status?: "PENDING" | "APPLIED" | "CONFLICT"
}

export interface MobileDashboardData {
  tasksCount: number
  eventsCount: number
  unreadNotificationsCount: number
  unreadEmailsCount: number
  recentTasks: Array<{ id: number; title: string; priority: string; status: string; due_date?: string }>
  upcomingEvents: Array<{ id: number; title: string; start_time: string; end_time?: string }>
  desktopStatus: {
    status: string
    version: string
    backend: string
    agent: string
    automations: string
  }
}

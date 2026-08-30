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

export interface RemoteCommandPayload {
  command_type: string
  parameters?: Record<string, any>
}

export interface RemotePendingAction {
  action_id: string
  request_id: string
  device_id: string
  command_type: string
  description: string
  risk_level: string
  status: string
  expires_at: string
}

export interface DesktopStatus {
  desktop_online: boolean
  app_version: string
  backend_status: string
  database_status: string
  sync_status: string
  pending_sync: number
  automations_status: string
  kill_switch_active: boolean
  notification_count: number
  tasks_count: number
  events_count: number
  last_seen: string
}

export interface MobileDashboardData {
  tasksCount: number
  eventsCount: number
  unreadNotificationsCount: number
  unreadEmailsCount: number
  recentTasks: Array<{ id: number; title: string; priority: string; status: string; due_date?: string }>
  upcomingEvents: Array<{ id: number; title: string; start_time: string; end_time?: string }>
  desktopStatus: DesktopStatus
}

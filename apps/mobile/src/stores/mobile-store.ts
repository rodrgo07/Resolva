import { create } from "zustand"
import { 
  ConnectivityState, DeviceInfo, MobileDashboardData, SyncOperationItem,
  DesktopStatus, RemotePendingAction, LiveSessionData, SyncConflictData
} from "../types"

interface MobileState {
  connectivity: ConnectivityState
  deviceInfo: DeviceInfo
  serverEndpoint: string
  sessionToken: string | null
  dashboard: MobileDashboardData | null
  desktopStatus: DesktopStatus | null
  pendingActions: RemotePendingAction[]
  offlineQueue: SyncOperationItem[]
  isSyncing: boolean
  liveSession: LiveSessionData | null
  conflicts: SyncConflictData[]
  lastEventSequence: number

  // Actions
  setConnectivity: (status: ConnectivityState) => void
  setServerEndpoint: (url: string) => void
  setSessionToken: (token: string | null) => void
  setDashboard: (data: MobileDashboardData) => void
  setDesktopStatus: (status: DesktopStatus) => void
  setPendingActions: (actions: RemotePendingAction[]) => void
  setLiveSession: (session: LiveSessionData | null) => void
  setConflicts: (conflicts: SyncConflictData[]) => void
  setLastEventSequence: (seq: number) => void
  enqueueOfflineOperation: (op: Omit<SyncOperationItem, "operation_id" | "device_id" | "version">) => void
  clearProcessedQueue: (operationIds: string[]) => void
  setDeviceInfo: (info: Partial<DeviceInfo>) => void
}

export const useMobileStore = create<MobileState>((set, get) => ({
  connectivity: "OFFLINE",
  serverEndpoint: "http://192.168.1.100:8700",
  sessionToken: null,
  isSyncing: false,
  deviceInfo: {
    deviceId: "RESOLVA-MOBILE-INIT",
    deviceName: "Meu Android",
    platform: "ANDROID",
    appVersion: "0.1.0",
    isPaired: false,
  },
  dashboard: null,
  desktopStatus: null,
  pendingActions: [],
  offlineQueue: [],
  liveSession: null,
  conflicts: [],
  lastEventSequence: 0,

  setConnectivity: (connectivity) => set({ connectivity }),
  setServerEndpoint: (serverEndpoint) => set({ serverEndpoint }),
  setSessionToken: (sessionToken) => set({ sessionToken }),
  setDashboard: (dashboard) => set({ dashboard }),
  setDesktopStatus: (desktopStatus) => set({ desktopStatus }),
  setPendingActions: (pendingActions) => set({ pendingActions }),
  setLiveSession: (liveSession) => set({ liveSession }),
  setConflicts: (conflicts) => set({ conflicts }),
  setLastEventSequence: (lastEventSequence) => set({ lastEventSequence }),
  setDeviceInfo: (info) => set((state) => ({ deviceInfo: { ...state.deviceInfo, ...info } })),

  enqueueOfflineOperation: (op) => {
    const { deviceInfo, offlineQueue } = get()
    const newOp: SyncOperationItem = {
      ...op,
      operation_id: "op_" + Date.now() + "_" + Math.random().toString(36).substring(2, 7),
      device_id: deviceInfo.deviceId,
      version: 1,
      created_at: new Date().toISOString(),
      status: "PENDING"
    }
    set({ offlineQueue: [...offlineQueue, newOp] })
  },


  clearProcessedQueue: (operationIds) => {
    set((state) => ({
      offlineQueue: state.offlineQueue.filter(op => !operationIds.includes(op.operation_id))
    }))
  }
}))

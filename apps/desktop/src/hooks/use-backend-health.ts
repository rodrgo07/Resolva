import { useEffect } from "react"
import { useAppStore } from "@/stores/app-store"
import { useNotificationStore } from "@/stores/notification-store"
import { api } from "@/lib/api-client"
import { Notification } from "@/types"

export function useBackendHealth() {
  const { setBackendStatus } = useAppStore()
  const { setNotifications } = useNotificationStore()

  useEffect(() => {
    let isMounted = true

    const checkHealth = async () => {
      try {
        const res = await api.get<{ status: string }>("/api/health")
        if (isMounted && res.status === "ok") {
          setBackendStatus("connected")
        }
      } catch {
        if (isMounted) {
          setBackendStatus("disconnected")
        }
      }
    }

    const fetchInitialNotifications = async () => {
      try {
        const data = await api.get<Notification[]>("/api/notifications/")
        if (isMounted && Array.isArray(data)) {
          setNotifications(data)
        }
      } catch {
        // Silently catch until backend is ready
      }
    }

    checkHealth()
    fetchInitialNotifications()

    const interval = setInterval(checkHealth, 15000)
    return () => {
      isMounted = false
      clearInterval(interval)
    }
  }, [setBackendStatus, setNotifications])
}

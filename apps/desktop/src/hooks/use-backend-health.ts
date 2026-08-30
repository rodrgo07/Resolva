import { useEffect, useRef } from "react"
import { useAppStore } from "@/stores/app-store"
import { useNotificationStore } from "@/stores/notification-store"
import { api } from "@/lib/api-client"
import { Notification } from "@/types"
import { BACKEND_STARTUP_DELAY_MS, BACKEND_MAX_RETRIES } from "@/lib/constants"

export function useBackendHealth() {
  const { setBackendStatus } = useAppStore()
  const { setNotifications } = useNotificationStore()
  const retryCount = useRef(0)
  const hasConnected = useRef(false)

  useEffect(() => {
    let isMounted = true
    let intervalId: ReturnType<typeof setInterval> | null = null

    const checkHealth = async () => {
      try {
        const res = await api.get<{ status: string }>("/api/health")
        if (isMounted && res.status === "ok") {
          setBackendStatus("connected")
          hasConnected.current = true
          retryCount.current = 0
          if (intervalId) {
            clearInterval(intervalId)
            intervalId = null
          }
        }
      } catch {
        if (isMounted) {
          if (hasConnected.current) {
            setBackendStatus("disconnected")
          } else if (retryCount.current < BACKEND_MAX_RETRIES) {
            setBackendStatus("connecting")
            retryCount.current++
          } else {
            setBackendStatus("disconnected")
          }
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

    // Delay initial check to allow backend subprocess to start
    const startupTimer = setTimeout(() => {
      if (!isMounted) return
      checkHealth()
      fetchInitialNotifications()

      // Poll every 15s after initial check
      intervalId = setInterval(checkHealth, 15000)
    }, BACKEND_STARTUP_DELAY_MS)

    return () => {
      isMounted = false
      clearTimeout(startupTimer)
      if (intervalId) clearInterval(intervalId)
    }
  }, [setBackendStatus, setNotifications])
}

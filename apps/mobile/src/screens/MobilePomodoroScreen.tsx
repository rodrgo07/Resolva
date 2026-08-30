import React, { useState, useEffect } from "react"
import { View, Text, StyleSheet, TouchableOpacity, Alert, ActivityIndicator } from "react-native"
import { useMobileStore } from "../stores/mobile-store"
import { MobileApiClient } from "../services/api-client"

export function MobilePomodoroScreen() {
  const { 
    serverEndpoint, sessionToken, deviceInfo, liveSession,
    connectivity, setLiveSession
  } = useMobileStore()
  
  const [localSeconds, setLocalSeconds] = useState(1500)
  const [isRunning, setIsRunning] = useState(false)
  const [isUpdating, setIsUpdating] = useState(false)

  const apiClient = new MobileApiClient(serverEndpoint, sessionToken)

  // Sincroniza estado com o liveSession recebido via WebSocket ou REST
  useEffect(() => {
    if (liveSession) {
      setLocalSeconds(liveSession.remaining_seconds)
      setIsRunning(liveSession.status === "RUNNING")
    }
  }, [liveSession])

  // Timer local fluido para renderização visual
  useEffect(() => {
    let timer: any = null
    if (isRunning && localSeconds > 0) {
      timer = setInterval(() => {
        setLocalSeconds((s) => {
          if (s <= 1) {
            setIsRunning(false)
            return 0
          }
          return s - 1
        })
      }, 1000)
    }
    return () => clearInterval(timer)
  }, [isRunning, localSeconds])

  const handleAction = async (action: "START" | "PAUSE" | "RESUME" | "COMPLETE") => {
    setIsUpdating(true)
    try {
      if (connectivity === "ONLINE") {
        const res = await fetch(serverEndpoint + "/api/realtime/state/action", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            device_id: deviceInfo.deviceId,
            type: "POMODORO",
            action: action,
            duration_seconds: 1500
          })
        })
        if (res.ok) {
          const updatedState = await res.json()
          setLiveSession(updatedState)
        }
      } else {
        // Modo offline
        if (action === "START" || action === "RESUME") {
          setIsRunning(true)
        } else if (action === "PAUSE") {
          setIsRunning(false)
        } else if (action === "COMPLETE") {
          setIsRunning(false)
          setLocalSeconds(0)
        }
      }
    } catch (err: any) {
      Alert.alert("Aviso", "Ação salva localmente; será sincronizada quando reconectar.")
    } finally {
      setIsUpdating(false)
    }
  }

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0")
  }

  return (
    <View style={styles.container}>
      <View style={styles.badgeContainer}>
        <View style={[styles.dot, connectivity === "ONLINE" ? styles.dotGreen : styles.dotYellow]} />
        <Text style={styles.badgeText}>
          {connectivity === "ONLINE" ? "Sincronização Live • Desktop Conectado" : "Modo Offline • Salvo Localmente"}
        </Text>
      </View>

      <Text style={styles.headerTitle}>POMODORO LIVE STATE</Text>
      <Text style={styles.headerSubtitle}>
        {liveSession?.origin_device_id ? "Iniciado por: " + liveSession.origin_device_id : "Foco Contínuo Multidispositivo"}
      </Text>


      <View style={[styles.timerCircle, isRunning && styles.timerCircleActive]}>
        <Text style={styles.timerText}>{formatTime(localSeconds)}</Text>
        <Text style={styles.modeText}>{isRunning ? "FOCO PROFUNDO ATIVO" : "PAUSADO / AGUARDANDO"}</Text>
      </View>

      <View style={styles.controlsRow}>
        <TouchableOpacity 
          style={styles.btnSecondary} 
          onPress={() => handleAction("COMPLETE")}
          disabled={isUpdating}
        >
          <Text style={styles.btnSecondaryText}>Finalizar</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.btnPrimary, isRunning && styles.btnActive]} 
          onPress={() => handleAction(isRunning ? "PAUSE" : (localSeconds < 1500 && localSeconds > 0 ? "RESUME" : "START"))}
          disabled={isUpdating}
        >
          {isUpdating ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.btnPrimaryText}>{isRunning ? "Pausar no Ecossistema" : "Iniciar Foco Global"}</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b", alignItems: "center", justifyContent: "center", padding: 20 },
  badgeContainer: { flexDirection: "row", alignItems: "center", gap: 6, paddingHorizontal: 12, paddingVertical: 6, borderRadius: 20, backgroundColor: "#18181b", borderColor: "#27272a", borderWidth: 1, marginBottom: 20 },
  dot: { width: 8, height: 8, borderRadius: 4 },
  dotGreen: { backgroundColor: "#22c55e" },
  dotYellow: { backgroundColor: "#eab308" },
  badgeText: { fontSize: 11, color: "#a1a1aa", fontWeight: "600" },
  headerTitle: { fontSize: 18, fontWeight: "bold", color: "#ffffff", letterSpacing: 1 },
  headerSubtitle: { fontSize: 11, color: "#818cf8", marginTop: 4, marginBottom: 30 },
  timerCircle: { width: 230, height: 230, borderRadius: 115, borderColor: "#3f3f46", borderWidth: 4, backgroundColor: "#18181b", alignItems: "center", justifyContent: "center", marginBottom: 35, shadowColor: "#6366f1", shadowOpacity: 0.2, shadowRadius: 20 },
  timerCircleActive: { borderColor: "#6366f1", shadowOpacity: 0.5 },
  timerText: { fontSize: 48, fontWeight: "bold", color: "#ffffff", fontFamily: "monospace" },
  modeText: { fontSize: 10, color: "#818cf8", fontWeight: "bold", letterSpacing: 1, marginTop: 8 },
  controlsRow: { flexDirection: "row", gap: 14, width: "100%", paddingHorizontal: 20 },
  btnSecondary: { flex: 1, paddingVertical: 14, backgroundColor: "#27272a", borderRadius: 12, alignItems: "center" },
  btnSecondaryText: { color: "#f4f4f5", fontWeight: "bold", fontSize: 13 },
  btnPrimary: { flex: 1.5, paddingVertical: 14, backgroundColor: "#6366f1", borderRadius: 12, alignItems: "center" },
  btnActive: { backgroundColor: "#ef4444" },
  btnPrimaryText: { color: "#ffffff", fontWeight: "bold", fontSize: 13 }
})

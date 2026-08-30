import React, { useState, useEffect } from "react"
import { View, Text, StyleSheet, TouchableOpacity, Alert } from "react-native"
import { useMobileStore } from "../stores/mobile-store"
import { MobileApiClient } from "../services/api-client"

export function MobilePomodoroScreen() {
  const { serverEndpoint, sessionToken, deviceInfo, enqueueOfflineOperation } = useMobileStore()
  const [timeLeft, setTimeLeft] = useState(25 * 60)
  const [isActive, setIsActive] = useState(false)
  const [mode, setMode] = useState<"foco" | "pausa">("foco")

  const apiClient = new MobileApiClient(serverEndpoint, sessionToken)

  useEffect(() => {
    let interval: any = null
    if (isActive && timeLeft > 0) {
      interval = setInterval(() => setTimeLeft((t) => t - 1), 1000)
    } else if (timeLeft === 0) {
      setIsActive(false)
      Alert.alert("Pomodoro Concluído!", mode === "foco" ? "Hora de uma pausa de 5 minutos." : "Pausa concluída! Pronto para o próximo foco?")
      
      // Registra sessão
      enqueueOfflineOperation({
        entity_type: "studies",
        entity_id: `pomo_${Date.now()}`,
        operation: "CREATE_STUDY_SESSION",
        payload: { duration_minutes: 25, mode: "pomodoro" }
      })
    }
    return () => clearInterval(interval)
  }, [isActive, timeLeft])

  const toggleTimer = async () => {
    if (!isActive) {
      // Inicia no Desktop remotamente se online
      try {
        await apiClient.executeRemoteCommand(deviceInfo.deviceId, {
          command_type: "START_POMODORO",
          parameters: { duration: 25 }
        })
      } catch {}
    }
    setIsActive(!isActive)
  }

  const resetTimer = () => {
    setIsActive(false)
    setTimeLeft(mode === "foco" ? 25 * 60 : 5 * 60)
  }

  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60)
    const s = seconds % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }

  return (
    <View style={styles.container}>
      <Text style={styles.headerTitle}>POMODORO TIMER</Text>
      <Text style={styles.headerSubtitle}>Sessão de Alta Concentração • Sincronização Ativa</Text>

      <View style={styles.timerCircle}>
        <Text style={styles.timerText}>{formatTime(timeLeft)}</Text>
        <Text style={styles.modeText}>{mode === "foco" ? "BLOCO DE FOCO" : "PAUSA CURTA"}</Text>
      </View>

      <View style={styles.controlsRow}>
        <TouchableOpacity style={styles.btnSecondary} onPress={resetTimer}>
          <Text style={styles.btnSecondaryText}>Reiniciar</Text>
        </TouchableOpacity>

        <TouchableOpacity style={[styles.btnPrimary, isActive && styles.btnActive]} onPress={toggleTimer}>
          <Text style={styles.btnPrimaryText}>{isActive ? "Pausar" : "Iniciar Foco"}</Text>
        </TouchableOpacity>
      </View>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b", alignItems: "center", justifyContent: "center", padding: 20 },
  headerTitle: { fontSize: 18, fontWeight: "bold", color: "#ffffff", letterSpacing: 1 },
  headerSubtitle: { fontSize: 11, color: "#a1a1aa", marginTop: 4, marginBottom: 40 },
  timerCircle: { width: 220, height: 220, borderRadius: 110, borderColor: "#6366f1", borderWidth: 4, backgroundColor: "#18181b", alignItems: "center", justifyContent: "center", marginBottom: 40, shadowColor: "#6366f1", shadowOpacity: 0.3, shadowRadius: 20 },
  timerText: { fontSize: 44, fontWeight: "bold", color: "#ffffff", fontFamily: "monospace" },
  modeText: { fontSize: 10, color: "#818cf8", fontWeight: "bold", letterSpacing: 1, marginTop: 8 },
  controlsRow: { flexDirection: "row", gap: 14, width: "100%", paddingHorizontal: 20 },
  btnSecondary: { flex: 1, paddingVertical: 14, backgroundColor: "#27272a", borderRadius: 12, alignItems: "center" },
  btnSecondaryText: { color: "#f4f4f5", fontWeight: "bold", fontSize: 13 },
  btnPrimary: { flex: 1.5, paddingVertical: 14, backgroundColor: "#6366f1", borderRadius: 12, alignItems: "center" },
  btnActive: { backgroundColor: "#ef4444" },
  btnPrimaryText: { color: "#ffffff", fontWeight: "bold", fontSize: 13 }
})

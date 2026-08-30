import React, { useState, useEffect } from "react"
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, ActivityIndicator, Alert } from "react-native"
import { useMobileStore } from "../stores/mobile-store"
import { MobileApiClient } from "../services/api-client"

export function MobileDashboardScreen() {
  const { 
    connectivity, deviceInfo, dashboard, desktopStatus, offlineQueue, 
    enqueueOfflineOperation, serverEndpoint, sessionToken, setDesktopStatus 
  } = useMobileStore()
  const [taskInput, setTaskInput] = useState("")
  const [isExecutingCommand, setIsExecutingCommand] = useState(false)
  const [commandFeedback, setCommandFeedback] = useState<string | null>(null)

  const apiClient = new MobileApiClient(serverEndpoint, sessionToken)

  useEffect(() => {
    // Carrega status espelhado do Desktop
    apiClient.getDesktopStatus()
      .then((st) => setDesktopStatus(st))
      .catch(() => {})
  }, [connectivity])

  const handleCreateQuickTask = () => {
    if (!taskInput.trim()) return
    
    // Adiciona na fila offline local-first imediatamente
    enqueueOfflineOperation({
      entity_type: "tasks",
      entity_id: `temp_${Date.now()}`,
      operation: "CREATE_TASK",
      payload: {
        title: taskInput.trim(),
        priority: "alta",
        status: "pendente"
      }
    })

    setTaskInput("")
  }

  const handleRemoteAction = async (cmdType: string, params: Record<string, any> = {}) => {
    setIsExecutingCommand(true)
    setCommandFeedback(null)
    try {
      const res = await apiClient.executeRemoteCommand(deviceInfo.deviceId, {
        command_type: cmdType,
        parameters: params
      })
      if (res.status === "PENDING_CONFIRMATION") {
        Alert.alert(
          "Confirmação Necessária",
          res.message,
          [
            { text: "Cancelar", style: "cancel" },
            { 
              text: "Confirmar", 
              onPress: async () => {
                const confRes = await apiClient.confirmRemoteAction(deviceInfo.deviceId, res.action_id!, true)
                setCommandFeedback(`✓ ${confRes.message}`)
              }
            }
          ]
        )
      } else {
        setCommandFeedback(`✓ ${res.message}`)
      }
    } catch (err: any) {
      setCommandFeedback(`✕ ${err.message}`)
    } finally {
      setIsExecutingCommand(false)
    }
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header com Identidade e Conectividade */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>RESOLVA MOBILE</Text>
          <Text style={styles.subGreeting}>{deviceInfo.deviceName} • v{deviceInfo.appVersion}</Text>
        </View>
        <View style={[styles.badge, connectivity === "ONLINE" ? styles.badgeOnline : styles.badgeOffline]}>
          <Text style={styles.badgeText}>{connectivity === "ONLINE" ? "● Desktop Conectado" : "○ Offline"}</Text>
        </View>
      </View>

      {/* Feedback de Comando Remoto */}
      {commandFeedback && (
        <View style={styles.feedbackBox}>
          <Text style={styles.feedbackText}>{commandFeedback}</Text>
        </View>
      )}

      {/* Card Controle do Desktop */}
      <View style={styles.cardDesktop}>
        <View style={styles.cardDesktopHeader}>
          <Text style={styles.cardDesktopLabel}>RESOLVA DESKTOP WINDOWS</Text>
          <Text style={styles.desktopStatusText}>
            {desktopStatus?.desktop_online ? "● Online" : "○ Desconectado"}
          </Text>
        </View>

        <Text style={styles.cardDesktopTitle}>
          Automações: {desktopStatus?.automations_status || "Ativas"} • Sync: {desktopStatus?.sync_status || "Online"}
        </Text>

        <View style={styles.remoteButtonsRow}>
          <TouchableOpacity 
            style={styles.btnRemoteAction} 
            onPress={() => handleRemoteAction("SYNC_NOW")}
            disabled={isExecutingCommand}
          >
            <Text style={styles.btnRemoteText}>Sincronizar</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.btnRemoteAction} 
            onPress={() => handleRemoteAction("CREATE_BACKUP")}
            disabled={isExecutingCommand}
          >
            <Text style={styles.btnRemoteText}>Criar Backup</Text>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.btnRemoteAction} 
            onPress={() => handleRemoteAction("START_POMODORO", { duration: 25 })}
            disabled={isExecutingCommand}
          >
            <Text style={styles.btnRemoteText}>Pomodoro (25m)</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Card Offline Status */}
      {offlineQueue.length > 0 && (
        <View style={styles.offlineBanner}>
          <Text style={styles.offlineBannerText}>
            ⚡ {offlineQueue.length} alteração(ões) pendente(s) salvas localmente.
          </Text>
        </View>
      )}

      {/* Resumo Rápido */}
      <View style={styles.statsRow}>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{dashboard?.tasksCount ?? 3}</Text>
          <Text style={styles.statLabel}>Tarefas</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{dashboard?.eventsCount ?? 2}</Text>
          <Text style={styles.statLabel}>Agenda</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{dashboard?.unreadEmailsCount ?? 1}</Text>
          <Text style={styles.statLabel}>E-mails</Text>
        </View>
        <View style={styles.statBox}>
          <Text style={styles.statNumber}>{dashboard?.unreadNotificationsCount ?? 4}</Text>
          <Text style={styles.statLabel}>Alertas</Text>
        </View>
      </View>

      {/* Quick Action: Nova Tarefa */}
      <View style={styles.quickActionBox}>
        <Text style={styles.sectionTitle}>Ação Rápida: Nova Tarefa</Text>
        <View style={styles.inputRow}>
          <TextInput
            style={styles.input}
            placeholder="O que você precisa resolver?"
            placeholderTextColor="#71717a"
            value={taskInput}
            onChangeText={setTaskInput}
          />
          <TouchableOpacity style={styles.btnPrimary} onPress={handleCreateQuickTask}>
            <Text style={styles.btnPrimaryText}>Adicionar</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b" },
  content: { padding: 20 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 16 },
  greeting: { fontSize: 20, fontWeight: "bold", color: "#f4f4f5", letterSpacing: 0.5 },
  subGreeting: { fontSize: 12, color: "#a1a1aa", marginTop: 2 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  badgeOnline: { backgroundColor: "rgba(16, 185, 129, 0.2)" },
  badgeOffline: { backgroundColor: "rgba(239, 68, 68, 0.2)" },
  badgeText: { fontSize: 11, fontWeight: "600", color: "#f4f4f5" },
  feedbackBox: { backgroundColor: "rgba(99, 102, 241, 0.15)", borderColor: "#6366f1", borderWidth: 1, padding: 10, borderRadius: 8, marginBottom: 14 },
  feedbackText: { color: "#c7d2fe", fontSize: 12, fontWeight: "600" },
  cardDesktop: { backgroundColor: "#18181b", borderColor: "#3f3f46", borderWidth: 1, borderRadius: 16, padding: 16, marginBottom: 18 },
  cardDesktopHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  cardDesktopLabel: { fontSize: 11, color: "#818cf8", fontWeight: "bold", letterSpacing: 1 },
  desktopStatusText: { fontSize: 11, color: "#10b981", fontWeight: "bold" },
  cardDesktopTitle: { fontSize: 13, color: "#e4e4e7", marginBottom: 12 },
  remoteButtonsRow: { flexDirection: "row", justifyContent: "space-between" },
  btnRemoteAction: { backgroundColor: "#27272a", paddingVertical: 8, paddingHorizontal: 10, borderRadius: 8, flex: 1, marginHorizontal: 3, alignItems: "center" },
  btnRemoteText: { color: "#f4f4f5", fontSize: 11, fontWeight: "600" },
  offlineBanner: { backgroundColor: "rgba(234, 179, 8, 0.15)", borderColor: "#eab308", borderWidth: 1, padding: 12, borderRadius: 10, marginBottom: 16 },
  offlineBannerText: { color: "#fef08a", fontSize: 12, fontWeight: "500" },
  statsRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 20 },
  statBox: { backgroundColor: "#18181b", flex: 1, marginHorizontal: 4, paddingVertical: 12, borderRadius: 12, alignItems: "center", borderColor: "#27272a", borderWidth: 1 },
  statNumber: { fontSize: 18, fontWeight: "bold", color: "#ffffff" },
  statLabel: { fontSize: 11, color: "#a1a1aa", marginTop: 4 },
  quickActionBox: { backgroundColor: "#18181b", padding: 16, borderRadius: 14, borderColor: "#27272a", borderWidth: 1, marginBottom: 20 },
  sectionTitle: { fontSize: 14, fontWeight: "bold", color: "#f4f4f5", marginBottom: 10 },
  inputRow: { flexDirection: "row", alignItems: "center" },
  input: { flex: 1, backgroundColor: "#27272a", color: "#ffffff", borderRadius: 8, paddingHorizontal: 12, height: 42, fontSize: 13, marginRight: 10 },
  btnPrimary: { backgroundColor: "#6366f1", paddingHorizontal: 16, height: 42, borderRadius: 8, justifyContent: "center", alignItems: "center" },
  btnPrimaryText: { color: "#ffffff", fontWeight: "bold", fontSize: 13 }
})

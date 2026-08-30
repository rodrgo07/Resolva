import React, { useState } from "react"
import { View, Text, StyleSheet, ScrollView, TouchableOpacity, TextInput, ActivityIndicator } from "react-native"
import { useMobileStore } from "../stores/mobile-store"
import { MobileApiClient } from "../services/api-client"

export function MobileDashboardScreen() {
  const { connectivity, deviceInfo, dashboard, offlineQueue, enqueueOfflineOperation, serverEndpoint, sessionToken } = useMobileStore()
  const [taskInput, setTaskInput] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleCreateQuickTask = () => {
    if (!taskInput.trim()) return
    setIsSubmitting(true)
    
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
    setIsSubmitting(false)
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header com Identidade e Conectividade */}
      <View style={styles.header}>
        <View>
          <Text style={styles.greeting}>BOM DIA, RODRIGO</Text>
          <Text style={styles.subGreeting}>RESOLVA MOBILE • {deviceInfo.deviceName}</Text>
        </View>
        <View style={[styles.badge, connectivity === "ONLINE" ? styles.badgeOnline : styles.badgeOffline]}>
          <Text style={styles.badgeText}>{connectivity === "ONLINE" ? "● Online" : "○ Offline"}</Text>
        </View>
      </View>

      {/* Card Offline Status */}
      {offlineQueue.length > 0 && (
        <View style={styles.offlineBanner}>
          <Text style={styles.offlineBannerText}>
            ⚡ {offlineQueue.length} alteração(ões) pendente(s) aguardando sincronização.
          </Text>
        </View>
      )}

      {/* Card AGORA */}
      <View style={styles.cardAgora}>
        <Text style={styles.cardAgoraLabel}>FOCO DE AGORA</Text>
        <Text style={styles.cardAgoraTitle}>Estudar para a Certificação Cloud</Text>
        <Text style={styles.cardAgoraSubtitle}>Prioridade Alta • Bloco de 45 minutos</Text>
      </View>

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

      {/* Recomendações do Agent */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Recomendações do Resolva Agent</Text>
        <View style={styles.agentCard}>
          <Text style={styles.agentCardTitle}>💡 Planejamento Sugerido</Text>
          <Text style={styles.agentCardDesc}>
            Você tem 2 reuniões no período da tarde. Sugiro concluir a proposta de consultoria pela manhã.
          </Text>
        </View>
      </View>
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b" },
  content: { padding: 20 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 20 },
  greeting: { fontSize: 20, fontWeight: "bold", color: "#f4f4f5", letterSpacing: 0.5 },
  subGreeting: { fontSize: 12, color: "#a1a1aa", marginTop: 2 },
  badge: { paddingHorizontal: 10, paddingVertical: 4, borderRadius: 12 },
  badgeOnline: { backgroundColor: "rgba(16, 185, 129, 0.2)" },
  badgeOffline: { backgroundColor: "rgba(239, 68, 68, 0.2)" },
  badgeText: { fontSize: 11, fontWeight: "600", color: "#f4f4f5" },
  offlineBanner: { backgroundColor: "rgba(234, 179, 8, 0.15)", borderColor: "#eab308", borderWidth: 1, padding: 12, borderRadius: 10, marginBottom: 16 },
  offlineBannerText: { color: "#fef08a", fontSize: 12, fontWeight: "500" },
  cardAgora: { backgroundColor: "#18181b", borderColor: "#6366f1", borderWidth: 1, borderRadius: 16, padding: 18, marginBottom: 20 },
  cardAgoraLabel: { fontSize: 11, color: "#818cf8", fontWeight: "bold", letterSpacing: 1, marginBottom: 6 },
  cardAgoraTitle: { fontSize: 17, fontWeight: "bold", color: "#ffffff" },
  cardAgoraSubtitle: { fontSize: 13, color: "#a1a1aa", marginTop: 4 },
  statsRow: { flexDirection: "row", justifyContent: "space-between", marginBottom: 24 },
  statBox: { backgroundColor: "#18181b", flex: 1, marginHorizontal: 4, paddingVertical: 14, borderRadius: 12, alignItems: "center", borderColor: "#27272a", borderWidth: 1 },
  statNumber: { fontSize: 18, fontWeight: "bold", color: "#ffffff" },
  statLabel: { fontSize: 11, color: "#a1a1aa", marginTop: 4 },
  quickActionBox: { backgroundColor: "#18181b", padding: 16, borderRadius: 14, borderColor: "#27272a", borderWidth: 1, marginBottom: 20 },
  section: { marginBottom: 20 },
  sectionTitle: { fontSize: 14, fontWeight: "bold", color: "#f4f4f5", marginBottom: 10 },
  inputRow: { flexDirection: "row", alignItems: "center" },
  input: { flex: 1, backgroundColor: "#27272a", color: "#ffffff", borderRadius: 8, paddingHorizontal: 12, height: 42, fontSize: 13, marginRight: 10 },
  btnPrimary: { backgroundColor: "#6366f1", paddingHorizontal: 16, height: 42, borderRadius: 8, justifyContent: "center", alignItems: "center" },
  btnPrimaryText: { color: "#ffffff", fontWeight: "bold", fontSize: 13 },
  agentCard: { backgroundColor: "rgba(99, 102, 241, 0.08)", borderColor: "rgba(99, 102, 241, 0.3)", borderWidth: 1, borderRadius: 12, padding: 14 },
  agentCardTitle: { color: "#c7d2fe", fontWeight: "bold", fontSize: 13, marginBottom: 4 },
  agentCardDesc: { color: "#a1a1aa", fontSize: 12, lineHeight: 18 }
})

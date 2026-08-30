import React, { useState, useEffect } from "react"
import { 
  View, Text, StyleSheet, FlatList, TouchableOpacity, 
  ActivityIndicator, Alert, ScrollView
} from "react-native"
import { useMobileStore } from "../stores/mobile-store"

interface OrchestrationRunItem {
  id: number
  run_id: string
  status: string
  trigger_type: string
  is_dry_run: boolean
  total_steps: number
  completed_steps: number
  created_at: string
}

interface WorkflowCandidateItem {
  workflow_id: string
  name: string
  score: number
  confidence: number
  priority: string
  reason: string
  factors: string[]
}

export function MobileOrchestrationScreen() {
  const { serverEndpoint, connectivity, deviceInfo } = useMobileStore()
  const [runs, setRuns] = useState<OrchestrationRunItem[]>([])
  const [recommendations, setRecommendations] = useState<WorkflowCandidateItem[]>([])
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      if (connectivity === "ONLINE") {
        const [runsRes, recRes] = await Promise.all([
          fetch(serverEndpoint + "/api/orchestration/runs?limit=10"),
          fetch(serverEndpoint + "/api/orchestration/recommendations")
        ])
        if (runsRes.ok) setRuns(await runsRes.json())
        if (recRes.ok) setRecommendations(await recRes.json())
      }
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [connectivity])

  const triggerOrchestration = async (isDryRun: boolean) => {
    try {
      const res = await fetch(serverEndpoint + "/api/orchestration/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trigger_type: "MANUAL",
          device_id: deviceInfo.deviceId,
          is_dry_run: isDryRun
        })
      })
      if (res.ok) {
        Alert.alert(
          isDryRun ? "Simulação Concluída" : "Orquestração Iniciada",
          isDryRun ? "Plano simulado com sucesso!" : "Workflows orquestrados em execução."
        )
        fetchData()
      }
    } catch {
      Alert.alert("Erro", "Falha ao acionar orquestração.")
    }
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>ORCHESTRATION INTELLIGENCE</Text>
        <Text style={styles.subtitle}>Coordenação Adaptativa & Planos Inteligentes</Text>
      </View>

      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.btnSimulate} onPress={() => triggerOrchestration(true)}>
          <Text style={styles.btnSimulateText}>Simular Plano (Dry Run)</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.btnRun} onPress={() => triggerOrchestration(false)}>
          <Text style={styles.btnRunText}>Executar Orquestração</Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 30 }} />
      ) : (
        <View style={styles.content}>
          <Text style={styles.sectionTitle}>RECOMENDAÇÕES CONTEXTUAIS ({recommendations.length})</Text>
          {recommendations.map((rec, idx) => (
            <View key={idx} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{rec.name}</Text>
                <View style={styles.scoreBadge}>
                  <Text style={styles.scoreText}>{rec.score} pts</Text>
                </View>
              </View>
              <Text style={styles.cardReason}>{rec.reason}</Text>
              {rec.factors?.map((f, fIdx) => (
                <Text key={fIdx} style={styles.factorText}>• {f}</Text>
              ))}
            </View>
          ))}

          <Text style={[styles.sectionTitle, { marginTop: 20 }]}>EXECUÇÕES RECENTES ({runs.length})</Text>
          {runs.map((r) => (
            <View key={r.run_id} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>Execução #{r.run_id.slice(-6)}</Text>
                <Text style={[styles.statusText, { color: r.status === "COMPLETED" ? "#4ade80" : "#f59e0b" }]}>
                  {r.status}
                </Text>
              </View>
              <Text style={styles.cardDesc}>
                Progresso: {r.completed_steps} de {r.total_steps} etapas concluídas
              </Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b", padding: 16 },
  header: { marginBottom: 16 },
  title: { fontSize: 18, fontWeight: "bold", color: "#ffffff" },
  subtitle: { fontSize: 11, color: "#818cf8", marginTop: 4 },
  actionRow: { flexDirection: "row", gap: 10, marginBottom: 16 },
  btnSimulate: { flex: 1, backgroundColor: "#27272a", paddingVertical: 10, borderRadius: 10, alignItems: "center" },
  btnSimulateText: { color: "#818cf8", fontSize: 12, fontWeight: "bold" },
  btnRun: { flex: 1, backgroundColor: "#4f46e5", paddingVertical: 10, borderRadius: 10, alignItems: "center" },
  btnRunText: { color: "#ffffff", fontSize: 12, fontWeight: "bold" },
  content: { paddingBottom: 40 },
  sectionTitle: { fontSize: 12, fontWeight: "bold", color: "#a1a1aa", marginBottom: 8, letterSpacing: 0.5 },
  card: { backgroundColor: "#18181b", borderColor: "#27272a", borderWidth: 1, borderRadius: 12, padding: 12, marginBottom: 10 },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  cardTitle: { fontSize: 13, fontWeight: "bold", color: "#f4f4f5" },
  scoreBadge: { backgroundColor: "#312e81", paddingHorizontal: 8, paddingVertical: 2, borderRadius: 8 },
  scoreText: { color: "#a5b4fc", fontSize: 10, fontWeight: "bold" },
  cardReason: { fontSize: 11, color: "#a1a1aa", marginTop: 4, marginBottom: 6 },
  factorText: { fontSize: 10, color: "#71717a", marginVertical: 1 },
  statusText: { fontSize: 11, fontWeight: "bold" },
  cardDesc: { fontSize: 11, color: "#71717a", marginTop: 4 }
})

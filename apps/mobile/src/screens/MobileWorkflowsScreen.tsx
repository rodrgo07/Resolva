import React, { useState, useEffect } from "react"
import { 
  View, Text, StyleSheet, FlatList, TouchableOpacity, 
  ActivityIndicator, Alert
} from "react-native"
import { useMobileStore } from "../stores/mobile-store"

interface WorkflowItem {
  id: number
  workflow_id: string
  name: string
  description?: string
  enabled: boolean
  status: string
  safety_level: string
  steps: Array<{ name: string; action_type: string }>
}

export function MobileWorkflowsScreen() {
  const { serverEndpoint, connectivity, deviceInfo } = useMobileStore()
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([])
  const [loading, setLoading] = useState(true)

  const fetchWorkflows = async () => {
    setLoading(true)
    try {
      if (connectivity === "ONLINE") {
        const res = await fetch(serverEndpoint + "/api/workflows")
        if (res.ok) {
          const data = await res.json()
          setWorkflows(data)
        }
      }
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchWorkflows()
  }, [connectivity])

  const toggleWorkflow = async (wf: WorkflowItem) => {
    const action = wf.enabled ? "pause" : "activate"
    try {
      const res = await fetch(serverEndpoint + "/api/workflows/" + wf.workflow_id + "/" + action, {
        method: "POST"
      })
      if (res.ok) {
        fetchWorkflows()
      }
    } catch {
      Alert.alert("Erro", "Não foi possível alterar o status do workflow.")
    }
  }

  const runTestWorkflow = async (wf: WorkflowItem) => {
    try {
      const res = await fetch(serverEndpoint + "/api/workflows/" + wf.workflow_id + "/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ device_id: deviceInfo.deviceId })
      })
      if (res.ok) {
        Alert.alert("Simulação Concluída", "Workflow testado em Dry Run com sucesso! Nenhuma alteração real foi feita.")
      }
    } catch {
      Alert.alert("Erro", "Falha ao testar workflow.")
    }
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>WORKFLOW INTELLIGENCE</Text>
        <Text style={styles.subtitle}>Automações Declarativas & Seguras</Text>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={workflows}
          keyExtractor={(item) => item.workflow_id}
          contentContainerStyle={styles.list}
          renderItem={({ item }) => (
            <View style={styles.card}>
              <View style={styles.cardHeader}>

                <View style={{ flex: 1 }}>
                  <Text style={styles.cardTitle}>{item.name}</Text>
                  {item.description ? <Text style={styles.cardDesc}>{item.description}</Text> : null}
                </View>
                <TouchableOpacity
                  onPress={() => toggleWorkflow(item)}
                  style={{
                    paddingHorizontal: 10,
                    paddingVertical: 4,
                    borderRadius: 12,
                    backgroundColor: item.enabled ? "#6366f1" : "#27272a"
                  }}
                >
                  <Text style={{ color: "#ffffff", fontSize: 10, fontWeight: "bold" }}>
                    {item.enabled ? "ATIVO" : "PAUSADO"}
                  </Text>
                </TouchableOpacity>
              </View>


              <View style={styles.stepsContainer}>
                <Text style={styles.stepsLabel}>ETAPAS ({item.steps?.length || 0}):</Text>
                {item.steps?.map((st, idx) => (
                  <Text key={idx} style={styles.stepItem}>• {st.name} ({st.action_type})</Text>
                ))}
              </View>


              <View style={styles.cardFooter}>
                <TouchableOpacity style={styles.btnTest} onPress={() => runTestWorkflow(item)}>
                  <Text style={styles.btnTestText}>Simular (Dry Run)</Text>
                </TouchableOpacity>
              </View>
            </View>
          )}
        />
      )}
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b", padding: 16 },
  header: { marginBottom: 20 },
  title: { fontSize: 18, fontWeight: "bold", color: "#ffffff", letterSpacing: 0.5 },
  subtitle: { fontSize: 11, color: "#818cf8", marginTop: 4 },
  list: { paddingBottom: 30 },
  card: { backgroundColor: "#18181b", borderColor: "#27272a", borderWidth: 1, borderRadius: 14, padding: 14, marginBottom: 12 },
  cardHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between" },
  cardTitle: { fontSize: 14, fontWeight: "bold", color: "#f4f4f5" },
  cardDesc: { fontSize: 11, color: "#a1a1aa", marginTop: 2 },
  stepsContainer: { marginTop: 10, paddingVertical: 8, borderTopWidth: 1, borderTopColor: "#27272a" },
  stepsLabel: { fontSize: 10, fontWeight: "bold", color: "#71717a", marginBottom: 4 },
  stepItem: { fontSize: 11, color: "#d4d4d8", marginVertical: 1 },
  cardFooter: { flexDirection: "row", justifyContent: "flex-end", marginTop: 10 },
  btnTest: { paddingHorizontal: 12, paddingVertical: 6, backgroundColor: "#27272a", borderRadius: 8 },
  btnTestText: { color: "#818cf8", fontSize: 11, fontWeight: "bold" }
})

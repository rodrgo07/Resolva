import React, { useState, useEffect } from "react"
import { 
  View, Text, StyleSheet, ScrollView, TouchableOpacity, 
  ActivityIndicator, Alert
} from "react-native"
import { useMobileStore } from "../stores/mobile-store"

interface ComponentHealth {
  component: string
  status: string
  latency_ms: number
  message: string
}

export function MobileSystemScreen() {
  const { serverEndpoint, connectivity, deviceInfo } = useMobileStore()
  const [healthData, setHealthData] = useState<any>(null)
  const [safetyState, setSafetyState] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = async () => {
    setLoading(true)
    try {
      if (connectivity === "ONLINE") {
        const [hRes, sRes] = await Promise.all([
          fetch(serverEndpoint + "/api/system/health"),
          fetch(serverEndpoint + "/api/system/safety")
        ])
        if (hRes.ok) setHealthData(await hRes.json())
        if (sRes.ok) setSafetyState(await sRes.json())
      }
    } catch {} finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [connectivity])

  const toggleSafeMode = async () => {
    if (!safetyState) return
    const newSafeMode = !safetyState.global_safe_mode
    try {
      const res = await fetch(serverEndpoint + "/api/system/safety", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ global_safe_mode: newSafeMode })
      })
      if (res.ok) {
        Alert.alert(
          newSafeMode ? "Modo Seguro Ativado" : "Modo Seguro Desativado",
          newSafeMode 
            ? "Operações destrutivas e automações de escrita foram suspensas." 
            : "Operação normal restabelecida."
        )
        fetchData()
      }
    } catch {
      Alert.alert("Erro", "Falha ao alterar Modo Seguro.")
    }
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.title}>SYSTEM & OBSERVABILITY</Text>
        <Text style={styles.subtitle}>Diagnóstico Central & Segurança Global</Text>
      </View>

      {/* Safe Mode Banner */}
      <View style={[styles.banner, { backgroundColor: safetyState?.global_safe_mode ? "#7f1d1d" : "#18181b" }]}>
        <View style={{ flex: 1 }}>
          <Text style={styles.bannerTitle}>
            {safetyState?.global_safe_mode ? "⚠️ SAFE_MODE ATIVO" : "🛡️ SISTEMA OPERACIONAL"}
          </Text>
          <Text style={styles.bannerDesc}>
            {safetyState?.global_safe_mode
              ? "Automações de modificação bloqueadas. Apenas leitura e simulação permitidas."
              : "Todas as políticas de autonomia e segurança operando normalmente."}
          </Text>
        </View>
        <TouchableOpacity style={styles.btnToggle} onPress={toggleSafeMode}>
          <Text style={styles.btnToggleText}>
            {safetyState?.global_safe_mode ? "Desativar" : "Ativar"}
          </Text>
        </TouchableOpacity>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color="#6366f1" style={{ marginTop: 30 }} />
      ) : (
        <View style={styles.content}>
          <Text style={styles.sectionTitle}>SUBSISTEMAS MONITORADOS</Text>
          {healthData?.components && Object.entries(healthData.components).map(([k, c]: [string, any]) => (
            <View key={k} style={styles.card}>
              <View style={styles.cardHeader}>
                <Text style={styles.cardTitle}>{c.component}</Text>
                <Text style={[styles.statusBadge, { color: c.status === "HEALTHY" ? "#4ade80" : "#f59e0b" }]}>
                  {c.status}
                </Text>
              </View>
              <Text style={styles.cardMessage}>{c.message}</Text>
              <Text style={styles.cardLatency}>Latência: {c.latency_ms}ms</Text>
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
  banner: { padding: 14, borderRadius: 12, borderWidth: 1, borderColor: "#27272a", flexDirection: "row", alignItems: "center", marginBottom: 16 },
  bannerTitle: { fontSize: 13, fontWeight: "bold", color: "#ffffff" },
  bannerDesc: { fontSize: 10, color: "#d4d4d8", marginTop: 2 },
  btnToggle: { backgroundColor: "#27272a", paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8, marginLeft: 10 },
  btnToggleText: { color: "#ffffff", fontSize: 11, fontWeight: "bold" },
  content: { paddingBottom: 40 },
  sectionTitle: { fontSize: 12, fontWeight: "bold", color: "#a1a1aa", marginBottom: 8, letterSpacing: 0.5 },
  card: { backgroundColor: "#18181b", borderColor: "#27272a", borderWidth: 1, borderRadius: 12, padding: 12, marginBottom: 10 },
  cardHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  cardTitle: { fontSize: 13, fontWeight: "bold", color: "#f4f4f5" },
  statusBadge: { fontSize: 11, fontWeight: "bold" },
  cardMessage: { fontSize: 11, color: "#a1a1aa", marginTop: 4 },
  cardLatency: { fontSize: 10, color: "#71717a", marginTop: 2 }
})

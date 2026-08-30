import React, { useState, useEffect, useRef } from "react"
import { 
  View, Text, StyleSheet, ScrollView, TextInput, TouchableOpacity, 
  ActivityIndicator, KeyboardAvoidingView, Platform, Alert 
} from "react-native"
import { useMobileStore } from "../stores/mobile-store"
import { MobileApiClient } from "../services/api-client"

interface ChatMessage {
  id: string
  sender: "user" | "agent"
  text: string
  timestamp: string
  toolTrace?: string
  requiresConfirmation?: boolean
  actionId?: string
}

export function MobileAgentScreen() {
  const { serverEndpoint, sessionToken, deviceInfo } = useMobileStore()
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "init",
      sender: "agent",
      text: "Olá Rodrigo! Sou o Resolva Agent. Como posso ajudar você hoje no seu computador ou no seu dia a dia?",
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const scrollViewRef = useRef<any>(null)

  const apiClient = new MobileApiClient(serverEndpoint, sessionToken)

  const handleSendMessage = async () => {
    if (!input.trim() || isLoading) return

    const userText = input.trim()
    const userMsg: ChatMessage = {
      id: `usr_${Date.now()}`,
      sender: "user",
      text: userText,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }

    setMessages((prev) => [...prev, userMsg])
    setInput("")
    setIsLoading(true)

    try {
      const response = await apiClient.askAgent(userText)
      const agentMsg: ChatMessage = {
        id: `agt_${Date.now()}`,
        sender: "agent",
        text: response.message || response.response || "Entendido, solicitação processada com sucesso.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        toolTrace: response.tool_calls ? JSON.stringify(response.tool_calls) : undefined,
        requiresConfirmation: response.requires_confirmation,
        actionId: response.action_id
      }
      setMessages((prev) => [...prev, agentMsg])
    } catch (err: any) {
      setMessages((prev) => [
        ...prev,
        {
          id: `err_${Date.now()}`,
          sender: "agent",
          text: `Não foi possível processar: ${err.message || "Servidor indisponível"}. Se estiver offline, ações locais de tarefas e despesas ainda podem ser salvas.`,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        }
      ])
    } finally {
      setIsLoading(false)
      setTimeout(() => scrollViewRef.current?.scrollToEnd({ animated: true }), 100)
    }
  }

  const handleConfirmAction = async (actionId: string, confirmed: boolean) => {
    try {
      const res = await apiClient.confirmRemoteAction(deviceInfo.deviceId, actionId, confirmed)
      Alert.alert("Confirmação", res.message)
    } catch (err: any) {
      Alert.alert("Erro", err.message)
    }
  }

  return (
    <KeyboardAvoidingView 
      style={styles.container} 
      behavior={Platform.OS === "ios" ? "padding" : undefined}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>RESOLVA AGENT</Text>
        <Text style={styles.headerSubtitle}>Permission Layer Ativa • Zero Shell</Text>
      </View>

      <ScrollView 
        ref={scrollViewRef} 
        style={styles.messagesContainer} 
        contentContainerStyle={styles.messagesContent}
      >
        {messages.map((m) => (
          <View 
            key={m.id} 
            style={[
              styles.messageBubble, 
              m.sender === "user" ? styles.userBubble : styles.agentBubble
            ]}
          >
            <Text style={styles.messageText}>{m.text}</Text>
            
            {m.toolTrace && (
              <View style={styles.toolTraceBox}>
                <Text style={styles.toolTraceLabel}>🔧 Ferramenta homologada executada</Text>
                <Text style={styles.toolTraceText}>{m.toolTrace}</Text>
              </View>
            )}

            {m.requiresConfirmation && m.actionId && (
              <View style={styles.confirmBox}>
                <Text style={styles.confirmTitle}>⚠️ Ação Protegida (MEDIUM/HIGH)</Text>
                <View style={styles.confirmButtons}>
                  <TouchableOpacity 
                    style={styles.btnReject} 
                    onPress={() => handleConfirmAction(m.actionId!, false)}
                  >
                    <Text style={styles.btnRejectText}>Cancelar</Text>
                  </TouchableOpacity>
                  <TouchableOpacity 
                    style={styles.btnConfirm} 
                    onPress={() => handleConfirmAction(m.actionId!, true)}
                  >
                    <Text style={styles.btnConfirmText}>Confirmar</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}

            <Text style={styles.timestamp}>{m.timestamp}</Text>
          </View>
        ))}

        {isLoading && (
          <View style={styles.loadingBubble}>
            <ActivityIndicator size="small" color="#818cf8" />
            <Text style={styles.loadingText}>Resolva Agent pensando...</Text>
          </View>
        )}
      </ScrollView>

      <View style={styles.inputContainer}>
        <TextInput
          style={styles.input}
          placeholder="Ex: o que tenho para hoje? ou crie uma tarefa..."
          placeholderTextColor="#71717a"
          value={input}
          onChangeText={setInput}
          multiline
        />
        <TouchableOpacity 
          style={[styles.sendButton, !input.trim() && styles.sendButtonDisabled]} 
          onPress={handleSendMessage}
          disabled={!input.trim() || isLoading}
        >
          <Text style={styles.sendButtonText}>Enviar</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b" },
  header: { padding: 16, borderBottomColor: "#27272a", borderBottomWidth: 1, backgroundColor: "#18181b" },
  headerTitle: { fontSize: 16, fontWeight: "bold", color: "#ffffff", letterSpacing: 0.5 },
  headerSubtitle: { fontSize: 11, color: "#818cf8", marginTop: 2 },
  messagesContainer: { flex: 1 },
  messagesContent: { padding: 16, gap: 12 },
  messageBubble: { maxWidth: "85%", padding: 14, borderRadius: 16 },
  userBubble: { alignSelf: "flex-end", backgroundColor: "#6366f1", borderBottomRightRadius: 4 },
  agentBubble: { alignSelf: "flex-start", backgroundColor: "#18181b", borderColor: "#27272a", borderWidth: 1, borderBottomLeftRadius: 4 },
  messageText: { color: "#ffffff", fontSize: 13.5, lineHeight: 20 },
  toolTraceBox: { marginTop: 8, padding: 8, backgroundColor: "rgba(0,0,0,0.3)", borderRadius: 8, borderColor: "#3f3f46", borderWidth: 1 },
  toolTraceLabel: { fontSize: 10, color: "#a1a1aa", fontWeight: "bold" },
  toolTraceText: { fontSize: 11, color: "#93c5fd", fontFamily: Platform.OS === "ios" ? "Menlo" : "monospace", marginTop: 2 },
  confirmBox: { marginTop: 10, padding: 10, backgroundColor: "rgba(234, 179, 8, 0.1)", borderColor: "#eab308", borderWidth: 1, borderRadius: 8 },
  confirmTitle: { fontSize: 11, color: "#fef08a", fontWeight: "bold", marginBottom: 6 },
  confirmButtons: { flexDirection: "row", gap: 8 },
  btnReject: { flex: 1, paddingVertical: 6, backgroundColor: "#27272a", borderRadius: 6, alignItems: "center" },
  btnRejectText: { color: "#e4e4e7", fontSize: 11, fontWeight: "bold" },
  btnConfirm: { flex: 1, paddingVertical: 6, backgroundColor: "#eab308", borderRadius: 6, alignItems: "center" },
  btnConfirmText: { color: "#000000", fontSize: 11, fontWeight: "bold" },
  timestamp: { fontSize: 10, color: "#71717a", alignSelf: "flex-end", marginTop: 4 },
  loadingBubble: { flexDirection: "row", alignItems: "center", gap: 8, padding: 12, backgroundColor: "#18181b", borderRadius: 12, alignSelf: "flex-start" },
  loadingText: { color: "#a1a1aa", fontSize: 12 },
  inputContainer: { flexDirection: "row", padding: 12, backgroundColor: "#18181b", borderTopColor: "#27272a", borderTopWidth: 1, alignItems: "center" },
  input: { flex: 1, backgroundColor: "#27272a", color: "#ffffff", borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, fontSize: 13, maxHeight: 100 },
  sendButton: { marginLeft: 10, backgroundColor: "#6366f1", paddingHorizontal: 16, paddingVertical: 10, borderRadius: 12 },
  sendButtonDisabled: { backgroundColor: "#3f3f46", opacity: 0.5 },
  sendButtonText: { color: "#ffffff", fontWeight: "bold", fontSize: 13 }
})

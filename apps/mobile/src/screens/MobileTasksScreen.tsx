import React, { useState } from "react"
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Modal, Alert } from "react-native"
import { useMobileStore } from "../stores/mobile-store"

interface TaskItem {
  id: string | number
  title: string
  priority: "alta" | "media" | "baixa"
  status: "pendente" | "concluida"
  dueDate?: string
}

export function MobileTasksScreen() {
  const { enqueueOfflineOperation, dashboard } = useMobileStore()
  const [tasks, setTasks] = useState<TaskItem[]>([
    { id: 1, title: "Estudar para Certificação Cloud", priority: "alta", status: "pendente", dueDate: "Hoje" },
    { id: 2, title: "Revisar proposta de consultoria", priority: "media", status: "pendente", dueDate: "Amanhã" },
    { id: 3, title: "Organizar extrato financeiro", priority: "baixa", status: "concluida", dueDate: "Ontem" },
  ])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [newTitle, setNewTitle] = useState("")
  const [newPriority, setNewPriority] = useState<"alta" | "media" | "baixa">("alta")

  const handleToggleTask = (task: TaskItem) => {
    const nextStatus = task.status === "pendente" ? "concluida" : "pendente"
    setTasks(tasks.map(t => t.id === task.id ? { ...t, status: nextStatus } : t))
    
    // Adiciona na fila offline de sincronização
    enqueueOfflineOperation({
      entity_type: "tasks",
      entity_id: String(task.id),
      operation: nextStatus === "concluida" ? "COMPLETE_TASK" : "UPDATE_TASK",
      payload: { task_id: task.id, status: nextStatus }
    })
  }

  const handleCreateTask = () => {
    if (!newTitle.trim()) return
    const newTask: TaskItem = {
      id: `local_${Date.now()}`,
      title: newTitle.trim(),
      priority: newPriority,
      status: "pendente",
      dueDate: "Hoje"
    }

    setTasks([newTask, ...tasks])
    enqueueOfflineOperation({
      entity_type: "tasks",
      entity_id: String(newTask.id),
      operation: "CREATE_TASK",
      payload: { title: newTask.title, priority: newTask.priority }
    })

    setNewTitle("")
    setIsModalOpen(false)
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>MINHAS TAREFAS</Text>
        <TouchableOpacity style={styles.btnAdd} onPress={() => setIsModalOpen(true)}>
          <Text style={styles.btnAddText}>+ Nova</Text>
        </TouchableOpacity>
      </View>

      <FlatList
        data={tasks}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <TouchableOpacity 
            style={[styles.taskCard, item.status === "concluida" && styles.taskCardDone]}
            onPress={() => handleToggleTask(item)}
          >
            <View style={[styles.checkbox, item.status === "concluida" && styles.checkboxDone]}>
              {item.status === "concluida" && <Text style={styles.checkmark}>✓</Text>}
            </View>
            <View style={styles.taskInfo}>
              <Text style={[styles.taskTitle, item.status === "concluida" && styles.taskTitleDone]}>
                {item.title}
              </Text>
              <View style={styles.badgeRow}>
                <Text style={[styles.priorityBadge, styles[`priority_${item.priority}`]]}>
                  {item.priority.toUpperCase()}
                </Text>
                {item.dueDate && <Text style={styles.dueText}>Prazo: {item.dueDate}</Text>}
              </View>
            </View>
          </TouchableOpacity>
        )}
      />

      <Modal visible={isModalOpen} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>Criar Nova Tarefa</Text>
            <TextInput
              style={styles.input}
              placeholder="Título da tarefa..."
              placeholderTextColor="#71717a"
              value={newTitle}
              onChangeText={setNewTitle}
            />

            <View style={styles.prioritySelector}>
              {(["alta", "media", "baixa"] as const).map((p) => (
                <TouchableOpacity 
                  key={p} 
                  style={[styles.priorityOption, newPriority === p && styles.priorityOptionActive]}
                  onPress={() => setNewPriority(p)}
                >
                  <Text style={[styles.priorityOptionText, newPriority === p && styles.priorityOptionTextActive]}>
                    {p.toUpperCase()}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.btnCancel} onPress={() => setIsModalOpen(false)}>
                <Text style={styles.btnCancelText}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.btnSave} onPress={handleCreateTask}>
                <Text style={styles.btnSaveText}>Salvar</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b" },
  header: { padding: 16, flexDirection: "row", justifyContent: "space-between", alignItems: "center", borderBottomColor: "#27272a", borderBottomWidth: 1, backgroundColor: "#18181b" },
  headerTitle: { fontSize: 16, fontWeight: "bold", color: "#ffffff", letterSpacing: 0.5 },
  btnAdd: { backgroundColor: "#6366f1", paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  btnAddText: { color: "#ffffff", fontWeight: "bold", fontSize: 12 },
  listContent: { padding: 16, gap: 10 },
  taskCard: { flexDirection: "row", alignItems: "center", padding: 14, backgroundColor: "#18181b", borderRadius: 12, borderColor: "#27272a", borderWidth: 1 },
  taskCardDone: { opacity: 0.5 },
  checkbox: { width: 22, height: 22, borderRadius: 6, borderColor: "#6366f1", borderWidth: 2, marginRight: 12, alignItems: "center", justifyContent: "center" },
  checkboxDone: { backgroundColor: "#6366f1" },
  checkmark: { color: "#ffffff", fontSize: 12, fontWeight: "bold" },
  taskInfo: { flex: 1 },
  taskTitle: { fontSize: 14, color: "#ffffff", fontWeight: "600" },
  taskTitleDone: { textDecorationLine: "line-through", color: "#71717a" },
  badgeRow: { flexDirection: "row", alignItems: "center", gap: 8, marginTop: 4 },
  priorityBadge: { fontSize: 9, fontWeight: "bold", paddingHorizontal: 6, paddingVertical: 2, borderRadius: 4 },
  priority_alta: { backgroundColor: "rgba(239, 68, 68, 0.2)", color: "#f87171" },
  priority_media: { backgroundColor: "rgba(234, 179, 8, 0.2)", color: "#facc15" },
  priority_baixa: { backgroundColor: "rgba(16, 185, 129, 0.2)", color: "#4ade80" },
  dueText: { fontSize: 11, color: "#71717a" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "center", padding: 20 },
  modalBox: { backgroundColor: "#18181b", padding: 20, borderRadius: 16, borderColor: "#3f3f46", borderWidth: 1 },
  modalTitle: { fontSize: 16, fontWeight: "bold", color: "#ffffff", marginBottom: 14 },
  input: { backgroundColor: "#27272a", color: "#ffffff", borderRadius: 8, padding: 12, fontSize: 13, marginBottom: 14 },
  prioritySelector: { flexDirection: "row", gap: 8, marginBottom: 16 },
  priorityOption: { flex: 1, paddingVertical: 8, borderRadius: 6, backgroundColor: "#27272a", alignItems: "center" },
  priorityOptionActive: { backgroundColor: "#6366f1" },
  priorityOptionText: { color: "#a1a1aa", fontSize: 11, fontWeight: "bold" },
  priorityOptionTextActive: { color: "#ffffff" },
  modalButtons: { flexDirection: "row", gap: 10 },
  btnCancel: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: "#27272a", alignItems: "center" },
  btnCancelText: { color: "#e4e4e7", fontWeight: "bold", fontSize: 12 },
  btnSave: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: "#6366f1", alignItems: "center" },
  btnSaveText: { color: "#ffffff", fontWeight: "bold", fontSize: 12 }
})

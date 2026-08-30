import React, { useState } from "react"
import { View, Text, StyleSheet, FlatList, TouchableOpacity, TextInput, Modal } from "react-native"
import { useMobileStore } from "../stores/mobile-store"

interface ExpenseItem {
  id: string | number
  description: string
  amount: number
  date: string
  type: "expense" | "income"
}

export function MobileFinancesScreen() {
  const { enqueueOfflineOperation } = useMobileStore()
  const [expenses, setExpenses] = useState<ExpenseItem[]>([
    { id: 1, description: "Almoço Executivo", amount: 45.90, date: "Hoje", type: "expense" },
    { id: 2, description: "Assinatura Nuvem", amount: 89.00, date: "Ontem", type: "expense" },
    { id: 3, description: "Reembolso Consultoria", amount: 350.00, date: "2 dias atrás", type: "income" },
  ])
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [desc, setDesc] = useState("")
  const [val, setVal] = useState("")

  const totalExpense = expenses.filter(e => e.type === "expense").reduce((acc, e) => acc + e.amount, 0)

  const handleCreateExpense = () => {
    if (!desc.trim() || !val.trim()) return
    const num = parseFloat(val.replace(",", "."))
    if (isNaN(num)) return

    const newExp: ExpenseItem = {
      id: `local_exp_${Date.now()}`,
      description: desc.trim(),
      amount: num,
      date: "Hoje",
      type: "expense"
    }

    setExpenses([newExp, ...expenses])
    enqueueOfflineOperation({
      entity_type: "finances",
      entity_id: String(newExp.id),
      operation: "CREATE_EXPENSE",
      payload: { description: newExp.description, amount: newExp.amount, type: "expense" }
    })

    setDesc("")
    setVal("")
    setIsModalOpen(false)
  }

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>FINANÇAS PESSOAIS</Text>
        <TouchableOpacity style={styles.btnAdd} onPress={() => setIsModalOpen(true)}>
          <Text style={styles.btnAddText}>+ Despesa</Text>
        </TouchableOpacity>
      </View>

      <View style={styles.summaryCard}>
        <Text style={styles.summaryLabel}>TOTAL DE DESPESAS (MÊS)</Text>
        <Text style={styles.summaryValue}>R$ {totalExpense.toFixed(2)}</Text>
      </View>

      <FlatList
        data={expenses}
        keyExtractor={(item) => String(item.id)}
        contentContainerStyle={styles.listContent}
        renderItem={({ item }) => (
          <View style={styles.expenseCard}>
            <View>
              <Text style={styles.expenseDesc}>{item.description}</Text>
              <Text style={styles.expenseDate}>{item.date}</Text>
            </View>
            <Text style={[styles.expenseAmount, item.type === "income" ? styles.incomeText : styles.expenseText]}>
              {item.type === "income" ? "+" : "-"} R$ {item.amount.toFixed(2)}
            </Text>
          </View>
        )}
      />

      <Modal visible={isModalOpen} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalBox}>
            <Text style={styles.modalTitle}>Registrar Nova Despesa</Text>
            <TextInput
              style={styles.input}
              placeholder="Descrição (ex: Café, Almoço)..."
              placeholderTextColor="#71717a"
              value={desc}
              onChangeText={setDesc}
            />
            <TextInput
              style={styles.input}
              placeholder="Valor (R$)..."
              placeholderTextColor="#71717a"
              keyboardType="numeric"
              value={val}
              onChangeText={setVal}
            />
            <View style={styles.modalButtons}>
              <TouchableOpacity style={styles.btnCancel} onPress={() => setIsModalOpen(false)}>
                <Text style={styles.btnCancelText}>Cancelar</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.btnSave} onPress={handleCreateExpense}>
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
  btnAdd: { backgroundColor: "#10b981", paddingHorizontal: 12, paddingVertical: 6, borderRadius: 8 },
  btnAddText: { color: "#ffffff", fontWeight: "bold", fontSize: 12 },
  summaryCard: { margin: 16, padding: 18, backgroundColor: "#18181b", borderRadius: 16, borderColor: "#27272a", borderWidth: 1 },
  summaryLabel: { fontSize: 11, color: "#a1a1aa", fontWeight: "bold", letterSpacing: 1 },
  summaryValue: { fontSize: 24, fontWeight: "bold", color: "#ffffff", marginTop: 4 },
  listContent: { paddingHorizontal: 16, gap: 10 },
  expenseCard: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", padding: 14, backgroundColor: "#18181b", borderRadius: 12, borderColor: "#27272a", borderWidth: 1 },
  expenseDesc: { fontSize: 14, color: "#ffffff", fontWeight: "600" },
  expenseDate: { fontSize: 11, color: "#71717a", marginTop: 2 },
  expenseAmount: { fontSize: 14, fontWeight: "bold" },
  expenseText: { color: "#f87171" },
  incomeText: { color: "#4ade80" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.7)", justifyContent: "center", padding: 20 },
  modalBox: { backgroundColor: "#18181b", padding: 20, borderRadius: 16, borderColor: "#3f3f46", borderWidth: 1 },
  modalTitle: { fontSize: 16, fontWeight: "bold", color: "#ffffff", marginBottom: 14 },
  input: { backgroundColor: "#27272a", color: "#ffffff", borderRadius: 8, padding: 12, fontSize: 13, marginBottom: 14 },
  modalButtons: { flexDirection: "row", gap: 10 },
  btnCancel: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: "#27272a", alignItems: "center" },
  btnCancelText: { color: "#e4e4e7", fontWeight: "bold", fontSize: 12 },
  btnSave: { flex: 1, paddingVertical: 10, borderRadius: 8, backgroundColor: "#10b981", alignItems: "center" },
  btnSaveText: { color: "#ffffff", fontWeight: "bold", fontSize: 12 }
})

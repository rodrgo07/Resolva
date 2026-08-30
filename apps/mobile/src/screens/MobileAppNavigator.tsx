import React, { useState } from "react"
import { View, Text, StyleSheet, TouchableOpacity, SafeAreaView } from "react-native"
import { MobileDashboardScreen } from "../components/MobileDashboardScreen"
import { MobileTasksScreen } from "./MobileTasksScreen"
import { MobileAgentScreen } from "./MobileAgentScreen"
import { MobilePomodoroScreen } from "./MobilePomodoroScreen"
import { MobileFinancesScreen } from "./MobileFinancesScreen"

export function MobileAppNavigator() {
  const [currentTab, setCurrentTab] = useState<"dashboard" | "tasks" | "agent" | "pomodoro" | "finances">("dashboard")

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenContainer}>
        {currentTab === "dashboard" && <MobileDashboardScreen />}
        {currentTab === "tasks" && <MobileTasksScreen />}
        {currentTab === "agent" && <MobileAgentScreen />}
        {currentTab === "pomodoro" && <MobilePomodoroScreen />}
        {currentTab === "finances" && <MobileFinancesScreen />}
      </View>

      <View style={styles.tabBar}>
        <TouchableOpacity 
          style={[styles.tabItem, currentTab === "dashboard" && styles.tabItemActive]} 
          onPress={() => setCurrentTab("dashboard")}
        >
          <Text style={[styles.tabText, currentTab === "dashboard" && styles.tabTextActive]}>Início</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, currentTab === "tasks" && styles.tabItemActive]} 
          onPress={() => setCurrentTab("tasks")}
        >
          <Text style={[styles.tabText, currentTab === "tasks" && styles.tabTextActive]}>Tarefas</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, currentTab === "agent" && styles.tabItemActive]} 
          onPress={() => setCurrentTab("agent")}
        >
          <Text style={[styles.tabText, currentTab === "agent" && styles.tabTextActive]}>Agent</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, currentTab === "pomodoro" && styles.tabItemActive]} 
          onPress={() => setCurrentTab("pomodoro")}
        >
          <Text style={[styles.tabText, currentTab === "pomodoro" && styles.tabTextActive]}>Estudos</Text>
        </TouchableOpacity>

        <TouchableOpacity 
          style={[styles.tabItem, currentTab === "finances" && styles.tabItemActive]} 
          onPress={() => setCurrentTab("finances")}
        >
          <Text style={[styles.tabText, currentTab === "finances" && styles.tabTextActive]}>Finanças</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  )
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#09090b" },
  screenContainer: { flex: 1 },
  tabBar: { flexDirection: "row", backgroundColor: "#18181b", borderTopColor: "#27272a", borderTopWidth: 1, paddingVertical: 8 },
  tabItem: { flex: 1, alignItems: "center", paddingVertical: 6 },
  tabItemActive: {},
  tabText: { fontSize: 11, color: "#71717a", fontWeight: "600" },
  tabTextActive: { color: "#6366f1", fontWeight: "bold" }
})

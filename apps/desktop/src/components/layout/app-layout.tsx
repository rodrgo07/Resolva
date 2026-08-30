import * as React from "react"
import { useEffect, Suspense, lazy } from "react"
import { Sidebar } from "./sidebar"
import { Topbar } from "./topbar"
import { CommandPalette } from "./command-palette"
import { 
  QuickTaskModal, QuickExpenseModal, QuickEventModal, QuickPomodoroModal 
} from "@/components/shared/quick-action-modals"
import { useAppStore } from "@/stores/app-store"
import { LoadingState } from "@/components/shared/loading-state"
import { useToast } from "@/components/ui/toast"
import { api } from "@/lib/api-client"

const DashboardPage = lazy(() => import("@/features/dashboard/page").then(m => ({ default: m.DashboardPage })))
const TasksPage = lazy(() => import("@/features/tasks/page").then(m => ({ default: m.TasksPage })))
const StudiesPage = lazy(() => import("@/features/studies/page").then(m => ({ default: m.StudiesPage })))
const FinancesPage = lazy(() => import("@/features/finances/page").then(m => ({ default: m.FinancesPage })))
const EmailsPage = lazy(() => import("@/features/emails/page").then(m => ({ default: m.EmailsPage })))
const CalendarPage = lazy(() => import("@/features/calendar/page").then(m => ({ default: m.CalendarPage })))
const AutomationsPage = lazy(() => import("@/features/automations/page").then(m => ({ default: m.AutomationsPage })))
const AIPage = lazy(() => import("@/features/ai/page").then(m => ({ default: m.AIPage })))
const ActivityPage = lazy(() => import("@/features/activity/page").then(m => ({ default: m.ActivityPage })))
const SettingsPage = lazy(() => import("@/features/settings/page").then(m => ({ default: m.SettingsPage })))
const NotificationsPage = lazy(() => import("@/features/notifications/page").then(m => ({ default: m.NotificationsPage })))

const pages: Record<string, React.LazyExoticComponent<React.ComponentType<any>>> = {
  dashboard: DashboardPage,
  tasks: TasksPage,
  studies: StudiesPage,
  finances: FinancesPage,
  emails: EmailsPage,
  calendar: CalendarPage,
  automations: AutomationsPage,
  ai: AIPage,
  activity: ActivityPage,
  settings: SettingsPage,
  notifications: NotificationsPage,
}

export function AppLayout() {
  const { 
    currentPage, setCurrentPage, isSearchOpen, setSearchOpen, toggleSearch,
    activeQuickModal, setActiveQuickModal 
  } = useAppStore()
  const { toast } = useToast()
  const CurrentPageComponent = pages[currentPage] || DashboardPage

  useEffect(() => {
    let unlistenHotkey: (() => void) | undefined
    let unlistenTray: (() => void) | undefined

    const setupListeners = async () => {
      try {
        const { listen } = await import("@tauri-apps/api/event")
        
        unlistenHotkey = await listen<string>("global-hotkey-triggered", (event) => {
          const action = event.payload
          if (action === "open_command_palette") {
            setSearchOpen(true)
          } else if (action === "open_quick_task") {
            setActiveQuickModal("task")
          } else if (action === "open_agent") {
            setCurrentPage("ai")
          } else if (action === "open_pomodoro") {
            setActiveQuickModal("pomodoro")
          }
        })

        unlistenTray = await listen<string>("tray-action", async (event) => {
          const action = event.payload
          if (action === "open_notifications") {
            setCurrentPage("notifications")
          } else if (action === "organize_my_day") {
            setCurrentPage("ai")
          } else if (action === "open_settings") {
            setCurrentPage("settings")
          } else if (action === "sync_now") {
            toast({ title: "Sincronização iniciada", description: "Verificando dados locais e remotos...", type: "info" })
            try {
              await api.post("/api/sync/trigger")
              toast({ title: "Sincronizado", description: "Todos os dados foram atualizados.", type: "success" })
            } catch (err: any) {
              toast({ title: "Erro na sincronização", description: err.message, type: "error" })
            }
          } else if (action === "create_backup") {
            toast({ title: "Criando backup...", description: "Criptografando estado do Resolva.", type: "info" })
            try {
              await api.post("/api/backups", { backup_type: "manual", encrypt: true })
              toast({ title: "Backup Realizado", description: "Cópia local gerada com sucesso.", type: "success" })
            } catch (err: any) {
              toast({ title: "Erro no backup", description: err.message, type: "error" })
            }
          } else if (action === "pause_automations") {
            try {
              await api.post("/api/automations/kill-switch/activate")
              toast({ title: "Kill Switch Ativado", description: "Todas as automações foram pausadas por segurança.", type: "warning" })
            } catch {}
          } else if (action === "resume_automations") {
            try {
              await api.post("/api/automations/kill-switch/deactivate")
              toast({ title: "Automações Retomadas", description: "O motor de rotinas voltou a operar normalmente.", type: "success" })
            } catch {}
          }
        })
      } catch (e) {}
    }

    setupListeners()

    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.code === "Space") {
        e.preventDefault()
        toggleSearch()
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toUpperCase() === "T") {
        e.preventDefault()
        setActiveQuickModal("task")
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toUpperCase() === "A") {
        e.preventDefault()
        setCurrentPage("ai")
      } else if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key.toUpperCase() === "P") {
        e.preventDefault()
        setActiveQuickModal("pomodoro")
      }
    }

    // Polling contínuo de Health Check do Backend
    const checkHealth = async () => {
      try {
        const res = await api.get<{ status: string }>("/api/health");
        if (res && res.status === "ok") {
          useAppStore.getState().setBackendStatus("connected");
        } else {
          useAppStore.getState().setBackendStatus("connecting");
        }
      } catch (err) {
        useAppStore.getState().setBackendStatus("disconnected");
      }
    };

    checkHealth();
    const healthInterval = setInterval(checkHealth, 5000);

    return () => {
      clearInterval(healthInterval);
      window.removeEventListener("keydown", handleKeyDown);
      if (unlistenHotkey) unlistenHotkey();
      if (unlistenTray) unlistenTray();
    };
  }, []);


  return (
    <div className="flex h-screen w-screen overflow-hidden bg-background text-text-primary font-sans selection:bg-accent/30">
      <Sidebar />
      <div className="flex flex-1 flex-col overflow-hidden relative">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-8 relative z-0">
          <div className="max-w-7xl mx-auto">
            <Suspense fallback={<LoadingState message="Carregando módulo..." />}>
              <CurrentPageComponent />
            </Suspense>
          </div>
        </main>
      </div>


      <CommandPalette isOpen={isSearchOpen} onClose={() => setSearchOpen(false)} />

      <QuickTaskModal 
        isOpen={activeQuickModal === "task"} 
        onClose={() => setActiveQuickModal(null)} 
      />
      <QuickExpenseModal 
        isOpen={activeQuickModal === "expense"} 
        onClose={() => setActiveQuickModal(null)} 
      />
      <QuickEventModal 
        isOpen={activeQuickModal === "event"} 
        onClose={() => setActiveQuickModal(null)} 
      />
      <QuickPomodoroModal 
        isOpen={activeQuickModal === "pomodoro"} 
        onClose={() => setActiveQuickModal(null)} 
      />
    </div>
  )
}

import { 
  LayoutDashboard, CheckSquare, BookOpen, Wallet, Mail, 
  CalendarDays, Zap, Bot, Activity, Settings, Bell, ChevronLeft, ChevronRight,
  RotateCcw, LucideIcon
} from "lucide-react"

import { cn } from "@/lib/utils"
import { useAppStore } from "@/stores/app-store"
import { useNotificationStore } from "@/stores/notification-store"
import { useState } from "react"

type Page =
  | "dashboard"
  | "tasks"
  | "studies"
  | "finances"
  | "emails"
  | "calendar"
  | "automations"
  | "ai"
  | "activity"
  | "settings"
  | "notifications"

interface NavItem {
  id: Page
  label: string
  icon: LucideIcon
}

const navItems: NavItem[] = [
  { id: "dashboard", label: "Dashboard", icon: LayoutDashboard },
  { id: "tasks", label: "Tarefas", icon: CheckSquare },
  { id: "studies", label: "Estudos", icon: BookOpen },
  { id: "finances", label: "Finanças", icon: Wallet },
  { id: "emails", label: "Emails", icon: Mail },
  { id: "calendar", label: "Agenda", icon: CalendarDays },
  { id: "automations", label: "Automações", icon: Zap },
  { id: "ai", label: "IA", icon: Bot },
  { id: "activity", label: "Atividade", icon: Activity },
]

export function Sidebar() {
  const { currentPage, setCurrentPage, backendStatus } = useAppStore()
  const { unreadCount } = useNotificationStore()
  const [isCollapsed, setIsCollapsed] = useState(false)

  const getStatusColor = () => {
    switch (backendStatus) {
      case "connected":
        return "bg-green-500 shadow-green-500/50 shadow-sm"
      case "connecting":
        return "bg-yellow-500 shadow-yellow-500/50 shadow-sm animate-pulse"
      case "disconnected":
        return "bg-red-500 shadow-red-500/50 shadow-sm"
      default:
        return "bg-surface-500"
    }
  }

  const getStatusLabel = () => {
    switch (backendStatus) {
      case "connected": return "Backend conectado"
      case "connecting": return "Conectando..."
      case "disconnected": return "Backend desconectado"
      default: return "Status desconhecido"
    }
  }

  return (
    <div 
      className={cn(
        "flex flex-col h-screen glass border-r border-border bg-sidebar-bg transition-all duration-300 relative select-none",
        isCollapsed ? "w-16" : "w-64"
      )}
    >
      <div className="flex h-16 items-center px-4 justify-between border-b border-border/40">
        {!isCollapsed && (
          <div className="flex items-center gap-2.5">
            <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-accent to-accent-light flex items-center justify-center font-black text-text-primary shadow-md shadow-accent-glow">
              R
            </div>
            <span className="font-extrabold text-lg tracking-wider text-text-primary">RESOLVA</span>
          </div>
        )}
        {isCollapsed && (
          <div className="h-8 w-8 rounded-xl bg-gradient-to-tr from-accent to-accent-light flex items-center justify-center font-black text-text-primary mx-auto shadow-md shadow-accent-glow">
            R
          </div>
        )}
        
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-text-secondary hover:text-text-primary p-1 rounded-md hover:bg-surface-hover absolute -right-3.5 top-5 bg-surface-elevated border border-border z-10 hidden sm:flex items-center justify-center shadow-md cursor-pointer"
        >
          {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1.5">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={cn(
              "flex items-center w-full px-3 py-2.5 rounded-xl transition-all group outline-none focus-visible:ring-2 focus-visible:ring-accent cursor-pointer",
              currentPage === item.id 
                ? "bg-accent/15 text-accent-light font-bold border border-accent/25 shadow-sm shadow-accent-glow" 
                : "text-text-secondary hover:bg-surface-hover/70 hover:text-text-primary"
            )}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className={cn("h-5 w-5 shrink-0", isCollapsed ? "mx-auto" : "mr-3", currentPage === item.id ? "text-accent-light" : "text-text-muted group-hover:text-text-primary")} />
            {!isCollapsed && <span className="text-sm">{item.label}</span>}
          </button>
        ))}
      </div>

      <div className="p-3 border-t border-border space-y-1.5">
        <button
          onClick={() => setCurrentPage("notifications")}
          className={cn(
            "flex items-center w-full px-3 py-2.5 rounded-xl transition-all relative outline-none focus-visible:ring-2 focus-visible:ring-accent cursor-pointer",
            currentPage === "notifications" ? "bg-accent/15 text-accent-light font-bold border border-accent/25" : "text-text-secondary hover:bg-surface-hover/70 hover:text-text-primary"
          )}
          title={isCollapsed ? "Notificações" : undefined}
        >
          <Bell className={cn("h-5 w-5 shrink-0", isCollapsed ? "mx-auto" : "mr-3", currentPage === "notifications" ? "text-accent-light" : "text-text-muted")} />
          {!isCollapsed && <span className="text-sm font-medium">Notificações</span>}
          {unreadCount > 0 && (
            <span className={cn(
              "absolute bg-accent text-text-primary text-[10px] font-bold rounded-full h-4 min-w-[16px] flex items-center justify-center px-1 shadow-sm",
              isCollapsed ? "top-1 right-2" : "right-3 top-3"
            )}>
              {unreadCount}
            </span>
          )}
        </button>
        
        <button
          onClick={() => setCurrentPage("settings")}
          className={cn(
            "flex items-center w-full px-3 py-2.5 rounded-xl transition-all outline-none focus-visible:ring-2 focus-visible:ring-accent cursor-pointer",
            currentPage === "settings" ? "bg-accent/15 text-accent-light font-bold border border-accent/25" : "text-text-secondary hover:bg-surface-hover/70 hover:text-text-primary"
          )}
          title={isCollapsed ? "Configurações" : undefined}
        >
          <Settings className={cn("h-5 w-5 shrink-0", isCollapsed ? "mx-auto" : "mr-3", currentPage === "settings" ? "text-accent-light" : "text-text-muted")} />
          {!isCollapsed && <span className="text-sm font-medium flex-1 text-left">Configurações</span>}
        </button>


        <div className={cn(
          "flex items-center justify-between py-2 px-3 rounded-lg bg-surface-elevated/40 border border-border text-xs",
          isCollapsed ? "justify-center" : "justify-between"
        )}>
          <div className="flex items-center gap-2">
            <div className={cn("h-2.5 w-2.5 rounded-full shrink-0", getStatusColor())} />
            {!isCollapsed && <span className="font-medium text-text-secondary">{getStatusLabel()}</span>}
          </div>
          {!isCollapsed && backendStatus === "disconnected" && (
            <button
              onClick={async () => {
                useAppStore.getState().setBackendStatus("connecting");
                try {
                  const { api } = await import("@/lib/api-client");
                  const res = await api.get<{ status: string }>("/api/health");
                  if (res && res.status === "ok") {
                    useAppStore.getState().setBackendStatus("connected");
                  }
                } catch {
                  useAppStore.getState().setBackendStatus("disconnected");
                }
              }}
              className="p-1 text-text-muted hover:text-accent-light transition-colors"
              title="Reconectar"
            >
              <RotateCcw size={12} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}


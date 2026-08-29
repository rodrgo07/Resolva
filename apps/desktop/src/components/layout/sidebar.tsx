import { 
  LayoutDashboard, CheckSquare, BookOpen, Wallet, Mail, 
  CalendarDays, Zap, Bot, Activity, Settings, Bell, ChevronLeft, ChevronRight,
  LucideIcon
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
        "flex flex-col h-screen glass border-r border-surface-700/50 bg-surface-900/60 transition-all duration-300 relative select-none",
        isCollapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex h-16 items-center px-4 justify-between">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="h-7 w-7 rounded-lg bg-accent-600 flex items-center justify-center font-bold text-white shadow-md shadow-accent-600/30">
              R
            </div>
            <span className="font-bold text-lg text-white tracking-wider">RESOLVA</span>
          </div>
        )}
        {isCollapsed && (
          <div className="h-7 w-7 rounded-lg bg-accent-600 flex items-center justify-center font-bold text-white mx-auto shadow-md shadow-accent-600/30">
            R
          </div>
        )}
        
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-surface-400 hover:text-white p-1 rounded-md hover:bg-surface-800 absolute -right-3.5 top-5 bg-surface-800 border border-surface-700 z-10 hidden sm:flex items-center justify-center shadow-md cursor-pointer"
        >
          {isCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-4 px-2 space-y-1">
        {navItems.map((item) => (
          <button
            key={item.id}
            onClick={() => setCurrentPage(item.id)}
            className={cn(
              "flex items-center w-full px-3 py-2.5 rounded-lg transition-colors group outline-none focus-visible:ring-2 focus-visible:ring-accent-500 cursor-pointer",
              currentPage === item.id 
                ? "bg-accent-500/20 text-accent-400 font-semibold" 
                : "text-surface-300 hover:bg-surface-800/50 hover:text-white"
            )}
            title={isCollapsed ? item.label : undefined}
          >
            <item.icon className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
            {!isCollapsed && <span className="text-sm font-medium">{item.label}</span>}
          </button>
        ))}
      </div>

      <div className="p-2 border-t border-surface-700/50 space-y-1">
        <button
          onClick={() => setCurrentPage("notifications")}
          className={cn(
            "flex items-center w-full px-3 py-2.5 rounded-lg transition-colors relative outline-none focus-visible:ring-2 focus-visible:ring-accent-500 cursor-pointer",
            currentPage === "notifications" ? "bg-accent-500/20 text-accent-400 font-semibold" : "text-surface-300 hover:bg-surface-800/50 hover:text-white"
          )}
          title={isCollapsed ? "Notificações" : undefined}
        >
          <Bell className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
          {!isCollapsed && <span className="text-sm font-medium">Notificações</span>}
          {unreadCount > 0 && (
            <span className={cn(
              "absolute bg-accent-500 text-white text-[10px] font-bold rounded-full h-4 min-w-[16px] flex items-center justify-center px-1 shadow-sm",
              isCollapsed ? "top-1 right-2" : "right-3 top-3"
            )}>
              {unreadCount}
            </span>
          )}
        </button>
        
        <button
          onClick={() => setCurrentPage("settings")}
          className={cn(
            "flex items-center w-full px-3 py-2.5 rounded-lg transition-colors outline-none focus-visible:ring-2 focus-visible:ring-accent-500 cursor-pointer",
            currentPage === "settings" ? "bg-accent-500/20 text-accent-400 font-semibold" : "text-surface-300 hover:bg-surface-800/50 hover:text-white"
          )}
          title={isCollapsed ? "Configurações" : undefined}
        >
          <Settings className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
          {!isCollapsed && <span className="text-sm font-medium flex-1 text-left">Configurações</span>}
        </button>

        <div className={cn(
          "flex items-center py-3 px-3",
          isCollapsed ? "justify-center" : "justify-start"
        )}>
          <div className={cn("h-2.5 w-2.5 rounded-full", getStatusColor())} />
          {!isCollapsed && <span className="ml-3 text-xs font-medium text-surface-400">{getStatusLabel()}</span>}
        </div>
      </div>
    </div>
  )
}

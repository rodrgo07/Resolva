import * as React from "react"
import { 
  LayoutDashboard, CheckSquare, BookOpen, Wallet, Mail, 
  CalendarDays, Zap, Bot, Activity, Settings, Bell, ChevronLeft, ChevronRight
} from "lucide-react"
import { cn } from "@/lib/utils"
import { useAppStore } from "@/stores/app-store"

const navItems = [
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
  const { currentPage, setCurrentPage } = useAppStore()
  const [isCollapsed, setIsCollapsed] = React.useState(false)
  const unreadCount = 3
  const backendStatus = "connected"

  const getStatusColor = () => {
    switch(backendStatus) {
      case "connected": return "bg-green-500"
      case "connecting": return "bg-yellow-500"
      case "disconnected": return "bg-red-500"
      default: return "bg-surface-500"
    }
  }

  return (
    <div 
      className={cn(
        "flex flex-col h-screen glass border-r border-surface-700/50 bg-surface-900/60 transition-all duration-300 relative",
        isCollapsed ? "w-16" : "w-60"
      )}
    >
      <div className="flex h-16 items-center px-4 justify-between">
        {!isCollapsed && <span className="font-bold text-lg text-accent-500 tracking-wider">RESOLVA</span>}
        {isCollapsed && <span className="font-bold text-lg text-accent-500 mx-auto">R</span>}
        
        <button 
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="text-surface-400 hover:text-white p-1 rounded-md hover:bg-surface-800 absolute -right-3.5 top-5 bg-surface-800 border border-surface-700 z-10 hidden sm:flex items-center justify-center shadow-md"
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
              "flex items-center w-full px-3 py-2.5 rounded-lg transition-colors group outline-none focus-visible:ring-2 focus-visible:ring-accent-500",
              currentPage === item.id 
                ? "bg-accent-500/20 text-accent-500" 
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
            "flex items-center w-full px-3 py-2.5 rounded-lg transition-colors relative outline-none focus-visible:ring-2 focus-visible:ring-accent-500",
            currentPage === "notifications" ? "bg-accent-500/20 text-accent-500" : "text-surface-300 hover:bg-surface-800/50 hover:text-white"
          )}
          title={isCollapsed ? "Notificações" : undefined}
        >
          <Bell className={cn("h-5 w-5", isCollapsed ? "mx-auto" : "mr-3")} />
          {!isCollapsed && <span className="text-sm font-medium">Notificações</span>}
          {unreadCount > 0 && (
            <span className={cn(
              "absolute bg-accent-500 text-white text-[10px] font-bold rounded-full h-4 min-w-[16px] flex items-center justify-center px-1",
              isCollapsed ? "top-1 right-2" : "right-3 top-3"
            )}>
              {unreadCount}
            </span>
          )}
        </button>
        
        <button
          onClick={() => setCurrentPage("settings")}
          className={cn(
            "flex items-center w-full px-3 py-2.5 rounded-lg transition-colors outline-none focus-visible:ring-2 focus-visible:ring-accent-500",
            currentPage === "settings" ? "bg-accent-500/20 text-accent-500" : "text-surface-300 hover:bg-surface-800/50 hover:text-white"
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
          <div className={cn("h-2.5 w-2.5 rounded-full shadow-sm", getStatusColor())} />
          {!isCollapsed && <span className="ml-3 text-xs font-medium text-surface-400">Backend conectado</span>}
        </div>
      </div>
    </div>
  )
}

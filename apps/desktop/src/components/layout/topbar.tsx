import { Search, Bell, Wifi, WifiOff, Loader2 } from "lucide-react"
import { useAppStore } from "@/stores/app-store"
import { useNotificationStore } from "@/stores/notification-store"
import { Button } from "@/components/ui/button"

const pageTitles: Record<string, string> = {
  dashboard: "Hoje",
  tasks: "Tarefas",
  studies: "Estudos",
  finances: "Finanças",
  emails: "Emails",
  calendar: "Agenda",
  automations: "Automações",
  ai: "Resolva AI",
  activity: "Atividade",
  settings: "Configurações",
  notifications: "Central de Notificações",
}

export function Topbar() {
  const { currentPage, setCurrentPage, setSearchOpen, backendStatus } = useAppStore()
  const { unreadCount } = useNotificationStore()
  const title = pageTitles[currentPage] || "Resolva"

  const statusConfig = {
    connected: { icon: Wifi, color: "text-green-400", label: "Backend online" },
    connecting: { icon: Loader2, color: "text-yellow-400", label: "Conectando..." },
    disconnected: { icon: WifiOff, color: "text-red-400", label: "Backend offline" },
  }
  const status = statusConfig[backendStatus]
  const StatusIcon = status.icon

  return (
    <header className="h-16 w-full flex items-center justify-between px-8 border-b border-border bg-surface/50 backdrop-blur-xl sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <h1 className="text-xl font-bold text-text-primary tracking-tight">{title}</h1>
        <div className={`flex items-center gap-1.5 px-2 py-1 rounded-lg text-[11px] font-medium ${status.color} bg-surface-hover/50`} title={status.label}>
          <StatusIcon className={`h-3 w-3 ${backendStatus === "connecting" ? "animate-spin" : ""}`} />
          <span className="hidden lg:inline">{status.label}</span>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          size="sm" 
          className="h-9 w-64 justify-start text-text-secondary border-border bg-surface-elevated/60 hidden md:flex hover:text-text-primary hover:border-accent/40 rounded-xl"
          onClick={() => setSearchOpen(true)}
        >
          <Search className="mr-2 h-4 w-4 text-accent-light" />
          <span>Buscar comandos...</span>
          <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-border bg-surface-hover px-1.5 text-[10px] font-medium text-text-muted">
            Ctrl+Space
          </kbd>
        </Button>
        
        <button 
          className="md:hidden p-2 text-text-secondary hover:text-text-primary rounded-xl hover:bg-surface-hover" 
          onClick={() => setSearchOpen(true)}
        >
          <Search className="h-5 w-5" />
        </button>

        {/* Quick Notification Bell */}
        <button
          onClick={() => setCurrentPage("notifications")}
          className="relative p-2 text-text-secondary hover:text-text-primary rounded-xl hover:bg-surface-hover transition-colors"
          title="Notificações"
        >
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 bg-accent text-text-primary text-[10px] font-bold rounded-full h-4 min-w-[16px] flex items-center justify-center px-1 shadow-sm animate-pulse">
              {unreadCount}
            </span>
          )}
        </button>

        <div className="h-8 w-8 rounded-xl overflow-hidden text-text-primary font-bold text-sm ml-1 ring-2 ring-border shadow-sm shadow-accent-glow cursor-pointer transition-transform hover:scale-105">
          <img 
            src="/resolvaLogo.jpg" 
            alt="Resolva" 
            className="h-full w-full object-cover" 
          />
        </div>
      </div>
    </header>
  )
}


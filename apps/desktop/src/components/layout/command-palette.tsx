import { useState, useEffect } from "react"
import { Modal } from "@/components/ui/modal"
import { 
  Search, CheckSquare, Wallet, CalendarDays, ArrowRight, Bot, Sparkles, 
  Mail, ShieldCheck, RefreshCw, Zap, Clock, ChevronRight, Bell, CheckCheck,
  AlertTriangle
} from "lucide-react"
import { useAppStore } from "@/stores/app-store"
import { api } from "@/lib/api-client"
import { useToast } from "@/components/ui/toast"
import { useNotificationStore } from "@/stores/notification-store"

interface SearchItem {
  id: number
  type: string
  title: string
  description: string
  url: string
}

export function CommandPalette({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [query, setQuery] = useState("")
  const [results, setResults] = useState<SearchItem[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [selectedIndex, setSelectedIndex] = useState(0)
  const { setCurrentPage, setActiveQuickModal } = useAppStore()
  const { markAllAsRead, fetchSummary } = useNotificationStore()
  const { toast } = useToast()

  const quickCommands = [
    { id: "new-task", title: "Criar nova tarefa", category: "Ações", icon: CheckSquare, color: "text-success", action: () => { onClose(); setActiveQuickModal("task"); } },
    { id: "new-expense", title: "Adicionar gasto", category: "Finanças", icon: Wallet, color: "text-success", action: () => { onClose(); setActiveQuickModal("expense"); } },
    { id: "new-event", title: "Adicionar compromisso", category: "Agenda", icon: CalendarDays, color: "text-accent-light", action: () => { onClose(); setActiveQuickModal("event"); } },
    { id: "pomodoro", title: "Iniciar Pomodoro", category: "Estudos", icon: Clock, color: "text-info", action: () => { onClose(); setActiveQuickModal("pomodoro"); } },
    
    // Notificações Inteligentes
    { id: "notifs", title: "Ver todas as notificações", category: "Notificações", icon: Bell, color: "text-accent-light", action: () => { onClose(); setCurrentPage("notifications"); } },
    { id: "notifs-read-all", title: "Marcar todas as notificações como lidas", category: "Notificações", icon: CheckCheck, color: "text-success", action: async () => { onClose(); try { await api.post("/api/notifications/read-all", {}); markAllAsRead(); fetchSummary(); toast({ title: "Notificações limpas", type: "success" }); } catch {} } },
    { id: "notifs-urgent", title: "Ver notificações urgentes", category: "Notificações", icon: AlertTriangle, color: "text-error", action: () => { onClose(); setCurrentPage("notifications"); } },
    
    // Planejamento & Agent
    { id: "organize", title: "Organizar meu dia (Planner)", category: "Agent", icon: Sparkles, color: "text-warning", action: () => { onClose(); setCurrentPage("ai"); } },
    { id: "agent", title: "Abrir Agent", category: "Agent", icon: Bot, color: "text-accent-light", action: () => { onClose(); setCurrentPage("ai"); } },
    
    // Módulos
    { id: "tasks", title: "Ver pendências / tarefas atrasadas", category: "Tarefas", icon: CheckSquare, color: "text-success", action: () => { onClose(); setCurrentPage("tasks"); } },
    { id: "emails", title: "Ver e-mails importantes", category: "E-mails", icon: Mail, color: "text-orange-400", action: () => { onClose(); setCurrentPage("emails"); } },
    
    // Sistema
    { id: "sync", title: "Sincronizar agora", category: "Sistema", icon: RefreshCw, color: "text-info", action: async () => { onClose(); toast({ title: "Sincronizando...", description: "Verificando dados locais e remotos.", type: "info" }); try { await api.post("/api/sync/trigger"); toast({ title: "Sincronizado", description: "Sincronização concluída com sucesso.", type: "success" }); } catch {} } },
    { id: "backup", title: "Criar backup", category: "Sistema", icon: ShieldCheck, color: "text-indigo-400", action: async () => { onClose(); toast({ title: "Criando backup...", description: "Criptografando banco de dados SQLite.", type: "info" }); try { await api.post("/api/backups", { backup_type: "manual", encrypt: true }); toast({ title: "Backup Criado", description: "Cópia segura gerada com sucesso.", type: "success" }); } catch {} } },
    { id: "automations", title: "Executar rotina / automações", category: "Automações", icon: Zap, color: "text-warning", action: () => { onClose(); setCurrentPage("automations"); } },
  ];

  const filteredCommands = query.trim()
    ? quickCommands.filter(c => c.title.toLowerCase().includes(query.toLowerCase()) || c.category.toLowerCase().includes(query.toLowerCase()))
    : quickCommands;

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
      setSelectedIndex(0)
      return
    }

    const timer = setTimeout(async () => {
      setIsLoading(true)
      try {
        const data = await api.get<{ results: SearchItem[] }>("/api/search/", { q: query })
        setResults(data.results || [])
      } catch {
        setResults([])
      } finally {
        setIsLoading(false)
      }
    }, 150)

    return () => clearTimeout(timer)
  }, [query])

  const totalItems = results.length > 0 ? results.length : filteredCommands.length;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowDown") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev + 1) % (totalItems || 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setSelectedIndex((prev) => (prev - 1 + (totalItems || 1)) % (totalItems || 1));
    } else if (e.key === "Enter") {
      e.preventDefault();
      if (results.length > 0 && results[selectedIndex]) {
        handleSelectSearchItem(results[selectedIndex]);
      } else if (filteredCommands[selectedIndex]) {
        filteredCommands[selectedIndex].action();
      }
    }
  };

  const handleSelectSearchItem = (item: SearchItem) => {
    onClose()
    if (item.url === "/tasks") setCurrentPage("tasks")
    else if (item.url === "/finances") setCurrentPage("finances")
    else if (item.url === "/studies") setCurrentPage("studies")
    else if (item.url === "/calendar") setCurrentPage("calendar")
    else if (item.url === "/emails") setCurrentPage("emails")
    else if (item.url === "/ai") setCurrentPage("ai")
    else if (item.url === "/notifications") setCurrentPage("notifications")
  }

  const groupedCategories = Array.from(new Set(filteredCommands.map(c => c.category)));

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="flex flex-col h-[520px] -m-6" onKeyDown={handleKeyDown}>
        <div className="flex items-center px-4 py-3.5 border-b border-border/80 bg-surface/60 backdrop-blur-md">
          <Search className="h-5 w-5 text-accent-light mr-3" />
          <input 
            autoFocus
            className="flex-1 bg-transparent border-none outline-none text-text-primary placeholder-surface-400 text-sm font-medium"
            placeholder="O que você quer resolver? (ex: Ver notificações, Criar tarefa, Organizar meu dia...)"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setSelectedIndex(0);
            }}
          />
          <div className="flex items-center space-x-1">
            <kbd className="hidden sm:inline-block pointer-events-none rounded border border-border bg-surface-elevated px-1.5 py-0.5 text-[10px] font-medium text-text-secondary">
              ↑↓ Navegar
            </kbd>
            <kbd className="hidden sm:inline-block pointer-events-none rounded border border-border bg-surface-elevated px-1.5 py-0.5 text-[10px] font-medium text-text-secondary">
              ↵ Enter
            </kbd>
            <kbd className="hidden sm:inline-block pointer-events-none rounded border border-border bg-surface-elevated px-1.5 py-0.5 text-[10px] font-medium text-text-secondary">
              ESC
            </kbd>
          </div>
        </div>

        <div className="flex-1 overflow-y-auto p-3 space-y-4">
          {isLoading ? (
            <div className="flex items-center justify-center h-full text-text-secondary text-sm">
              Pesquisando no Resolva...
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-1">
              <div className="px-2 py-1 text-xs font-semibold text-text-secondary uppercase tracking-wider">
                Resultados da Busca
              </div>
              {results.map((item, idx) => {
                const isSelected = idx === selectedIndex;
                return (
                  <button 
                    key={`${item.type}-${item.id}`}
                    className={`w-full flex items-center px-3 py-2.5 rounded-lg text-left group transition-all outline-none ${
                      isSelected ? "bg-accent/20 border border-accent/40 text-text-primary" : "hover:bg-surface-elevated text-text-primary"
                    }`}
                    onClick={() => handleSelectSearchItem(item)}
                  >
                    <div className="h-8 w-8 rounded-md bg-surface-elevated flex items-center justify-center mr-3 border border-border/50 text-accent-light">
                      <Search className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-text-primary truncate">{item.title}</div>
                      <div className="text-xs text-text-secondary truncate">{item.description}</div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-text-muted opacity-60" />
                  </button>
                );
              })}
            </div>
          ) : (
            <div className="space-y-4">
              {groupedCategories.map((cat) => {
                const items = filteredCommands.filter(c => c.category === cat);
                return (
                  <div key={cat} className="space-y-1">
                    <div className="px-2 py-1 text-[11px] font-bold text-text-secondary uppercase tracking-wider">
                      {cat}
                    </div>
                    {items.map((cmd) => {
                      const globalIdx = filteredCommands.indexOf(cmd);
                      const isSelected = globalIdx === selectedIndex;
                      return (
                        <button
                          key={cmd.id}
                          className={`w-full flex items-center px-3 py-2 rounded-lg text-left transition-colors ${
                            isSelected ? "bg-accent/20 border border-accent/40 text-text-primary" : "hover:bg-surface-elevated/70 text-text-primary"
                          }`}
                          onClick={cmd.action}
                        >
                          <div className="h-7 w-7 rounded-md bg-surface-elevated/80 flex items-center justify-center mr-3 text-text-secondary border border-border/50">
                            <cmd.icon className={`h-3.5 w-3.5 ${cmd.color}`} />
                          </div>
                          <span className="text-sm font-medium flex-1">{cmd.title}</span>
                          <ChevronRight className="h-3.5 w-3.5 text-text-muted opacity-40" />
                        </button>
                      );
                    })}
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </Modal>
  )
}

import { useState, useEffect } from "react"
import { Modal } from "@/components/ui/modal"
import { Search, CheckSquare, BookOpen, Wallet, CalendarDays, ArrowRight, Bot, Sparkles, Mail } from "lucide-react"
import { useAppStore } from "@/stores/app-store"
import { api } from "@/lib/api-client"

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
  const { setCurrentPage } = useAppStore()

  useEffect(() => {
    if (!query.trim()) {
      setResults([])
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
    }, 200)

    return () => clearTimeout(timer)
  }, [query])

  const getIcon = (type: string) => {
    switch (type) {
      case "task": return CheckSquare
      case "finance": return Wallet
      case "study": return BookOpen
      case "calendar": return CalendarDays
      case "email": return Mail
      default: return Search
    }
  }

  const handleSelect = (item: SearchItem) => {
    onClose()
    if (item.url === "/tasks") setCurrentPage("tasks")
    else if (item.url === "/finances") setCurrentPage("finances")
    else if (item.url === "/studies") setCurrentPage("studies")
    else if (item.url === "/calendar") setCurrentPage("calendar")
    else if (item.url === "/emails") setCurrentPage("emails")
    else if (item.url === "/ai") setCurrentPage("ai")
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="flex flex-col h-[440px] -m-6">
        <div className="flex items-center px-4 py-3 border-b border-surface-700 bg-surface-900/50">
          <Search className="h-5 w-5 text-surface-400 mr-3" />
          <input 
            autoFocus
            className="flex-1 bg-transparent border-none outline-none text-white placeholder-surface-400 text-sm"
            placeholder="Buscar tarefas, e-mails, gastos ou comandos do Agent..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <kbd className="hidden sm:inline-block pointer-events-none rounded border border-surface-700 bg-surface-800 px-1.5 py-0.5 text-[10px] font-medium text-surface-300">
            ESC
          </kbd>
        </div>

        <div className="flex-1 overflow-y-auto p-3">
          {isLoading ? (
            <div className="flex items-center justify-center h-full text-surface-400 text-sm">
              Pesquisando no Resolva...
            </div>
          ) : results.length > 0 ? (
            <div className="space-y-1">
              <div className="px-2 py-1 text-xs font-semibold text-surface-400 uppercase tracking-wider">
                Resultados
              </div>
              {results.map((item) => {
                const Icon = getIcon(item.type)
                return (
                  <button 
                    key={`${item.type}-${item.id}`}
                    className="w-full flex items-center px-3 py-2.5 rounded-lg hover:bg-surface-800 text-left group transition-colors focus:bg-surface-800 outline-none"
                    onClick={() => handleSelect(item)}
                  >
                    <div className="h-9 w-9 rounded-md bg-surface-800 group-hover:bg-surface-700 flex items-center justify-center mr-3 transition-colors border border-surface-700/50 text-accent-400">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-sm font-medium text-white truncate">{item.title}</div>
                      <div className="text-xs text-surface-400 truncate">{item.description}</div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </button>
                )
              })}
            </div>
          ) : query ? (
            <div className="flex flex-col items-center justify-center h-full text-surface-400 p-8 text-center">
              <Search className="h-8 w-8 mb-3 opacity-30" />
              <p className="text-sm">Nenhum resultado encontrado para "{query}"</p>
            </div>
          ) : (
            <div className="space-y-1">
              <div className="px-2 py-1 text-xs font-semibold text-surface-400 uppercase tracking-wider">
                Comandos do Resolva Agent
              </div>
              {[
                { title: "Perguntar ao Resolva Agent", page: "ai" as const, icon: Bot, color: "text-accent-400" },
                { title: "Organizar meu dia (Planner)", page: "ai" as const, icon: Sparkles, color: "text-yellow-400" },
                { title: "Ver tarefas e pendências", page: "tasks" as const, icon: CheckSquare, color: "text-emerald-400" },
                { title: "Ver e-mails prioritários (Gmail + Outlook)", page: "emails" as const, icon: Mail, color: "text-orange-400" },
                { title: "Consultar finanças", page: "finances" as const, icon: Wallet, color: "text-green-400" },
                { title: "Iniciar estudos (Pomodoro)", page: "studies" as const, icon: BookOpen, color: "text-blue-400" },
              ].map((act, i) => (
                <button
                  key={i}
                  className="w-full flex items-center px-3 py-2.5 rounded-lg hover:bg-surface-800 text-left group transition-colors"
                  onClick={() => {
                    setCurrentPage(act.page)
                    onClose()
                  }}
                >
                  <div className="h-8 w-8 rounded-md bg-surface-800 flex items-center justify-center mr-3 text-surface-300">
                    <act.icon className={`h-4 w-4 ${act.color}`} />
                  </div>
                  <span className="text-sm text-surface-200">{act.title}</span>
                </button>
              ))}
            </div>
          )}
        </div>
      </div>
    </Modal>
  )
}

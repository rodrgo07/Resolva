import * as React from "react"
import { Search } from "lucide-react"
import { useAppStore } from "@/stores/app-store"
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
  notifications: "Notificações",
}

export function Topbar() {
  const { currentPage, setSearchOpen } = useAppStore()
  const title = pageTitles[currentPage] || "Resolva"
  
  return (
    <header className="h-16 w-full flex items-center justify-between px-8 border-b border-surface-800/50 bg-surface-900/30 backdrop-blur-md sticky top-0 z-30">
      <h1 className="text-xl font-semibold text-white tracking-tight">{title}</h1>
      
      <div className="flex items-center gap-4">
        <Button 
          variant="outline" 
          size="sm" 
          className="h-9 w-64 justify-start text-surface-400 border-surface-700/50 bg-surface-900/50 hidden md:flex hover:text-white"
          onClick={() => setSearchOpen(true)}
        >
          <Search className="mr-2 h-4 w-4" />
          <span>Buscar comandos...</span>
          <kbd className="ml-auto pointer-events-none inline-flex h-5 select-none items-center gap-1 rounded border border-surface-700 bg-surface-800 px-1.5 text-[10px] font-medium text-surface-300">
            Ctrl+K
          </kbd>
        </Button>
        
        <button className="md:hidden p-2 text-surface-400 hover:text-white rounded-md hover:bg-surface-800" onClick={() => setSearchOpen(true)}>
          <Search className="h-5 w-5" />
        </button>

        <div className="h-8 w-8 rounded-full bg-accent-600 flex items-center justify-center text-white font-medium text-sm ml-2 ring-2 ring-surface-800 cursor-pointer hover:bg-accent-700 transition-colors">
          U
        </div>
      </div>
    </header>
  )
}

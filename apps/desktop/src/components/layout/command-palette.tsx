import * as React from "react"
import { Modal } from "@/components/ui/modal"
import { Search, CheckSquare, BookOpen, Wallet, Mail, Settings } from "lucide-react"

export function CommandPalette({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) {
  const [query, setQuery] = React.useState("")
  
  const results = [
    { id: 1, title: "Nova Tarefa", subtitle: "Criar uma nova tarefa", icon: CheckSquare, category: "Tarefas" },
    { id: 2, title: "Iniciar Sessão de Estudo", subtitle: "Pomodoro de 25m", icon: BookOpen, category: "Estudos" },
    { id: 3, title: "Adicionar Despesa", subtitle: "Registrar gasto", icon: Wallet, category: "Finanças" },
    { id: 4, title: "Checar Emails", subtitle: "Sincronizar caixa de entrada", icon: Mail, category: "Emails" },
    { id: 5, title: "Preferências", subtitle: "Alterar configurações do app", icon: Settings, category: "Configurações" },
  ].filter(r => r.title.toLowerCase().includes(query.toLowerCase()) || r.subtitle.toLowerCase().includes(query.toLowerCase()))

  return (
    <Modal isOpen={isOpen} onClose={onClose} size="lg">
      <div className="flex flex-col h-[400px] -m-6">
        <div className="flex items-center px-4 py-3 border-b border-surface-700">
          <Search className="h-5 w-5 text-surface-400 mr-3" />
          <input 
            autoFocus
            className="flex-1 bg-transparent border-none outline-none text-white placeholder-surface-400"
            placeholder="Buscar comandos, arquivos ou ações..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <kbd className="hidden sm:inline-block pointer-events-none rounded border border-surface-700 bg-surface-800 px-1.5 py-0.5 text-[10px] font-medium text-surface-300">
            ESC
          </kbd>
        </div>
        <div className="flex-1 overflow-y-auto p-2">
          {results.length > 0 ? (
            <div className="space-y-1 mt-2">
              <div className="px-3 py-1 text-xs font-semibold text-surface-400 uppercase tracking-wider mb-2">
                Sugestões
              </div>
              {results.map((result) => (
                <button 
                  key={result.id}
                  className="w-full flex items-center px-3 py-3 rounded-lg hover:bg-surface-800 text-left group transition-colors focus:bg-surface-800 outline-none"
                  onClick={() => {
                    onClose()
                  }}
                >
                  <div className="h-10 w-10 rounded-md bg-surface-800 group-hover:bg-surface-700 flex items-center justify-center mr-4 transition-colors border border-surface-700/50">
                    <result.icon className="h-5 w-5 text-surface-300 group-hover:text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-medium text-white">{result.title}</div>
                    <div className="text-xs text-surface-400 mt-0.5">{result.subtitle}</div>
                  </div>
                  <div className="text-xs text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1">
                    Enter <kbd className="font-sans text-[10px]">↵</kbd>
                  </div>
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-surface-400 p-8 text-center">
              <Search className="h-8 w-8 mb-4 opacity-30" />
              <p>Nenhum resultado encontrado para "{query}"</p>
            </div>
          )}
        </div>
      </div>
    </Modal>
  )
}

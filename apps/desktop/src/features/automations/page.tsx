import { Zap, Plus } from "lucide-react";

export function AutomationsPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-50">Automações</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Nova automação
        </button>
      </div>

      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="p-4 rounded-full bg-surface-800/50 mb-4">
          <Zap className="w-10 h-10 text-surface-600" />
        </div>
        <h3 className="text-lg font-medium text-surface-300 mb-2">
          Nenhuma automação criada
        </h3>
        <p className="text-sm text-surface-500 mb-6 max-w-sm">
          Crie automações para abrir aplicativos, executar comandos e organizar seu fluxo de trabalho.
        </p>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Criar automação
        </button>
      </div>
    </div>
  );
}

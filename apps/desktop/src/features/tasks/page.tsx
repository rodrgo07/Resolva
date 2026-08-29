import { useState } from "react";
import { Plus, Filter, CheckSquare } from "lucide-react";

export function TasksPage() {
  const [_filter, setFilter] = useState("all");

  const filters = [
    { key: "all", label: "Todas" },
    { key: "today", label: "Hoje" },
    { key: "overdue", label: "Atrasadas" },
    { key: "high", label: "Alta prioridade" },
    { key: "completed", label: "Concluídas" },
  ];

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-50">Tarefas</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Nova tarefa
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-surface-500" />
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${
              _filter === f.key
                ? "bg-accent-500/10 text-accent-400 border border-accent-500/20"
                : "text-surface-400 hover:text-surface-200 hover:bg-surface-800"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Empty State */}
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="p-4 rounded-full bg-surface-800/50 mb-4">
          <CheckSquare className="w-10 h-10 text-surface-600" />
        </div>
        <h3 className="text-lg font-medium text-surface-300 mb-2">
          Nenhuma tarefa encontrada
        </h3>
        <p className="text-sm text-surface-500 mb-6 max-w-sm">
          Comece criando sua primeira tarefa para organizar seu dia.
        </p>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Criar tarefa
        </button>
      </div>
    </div>
  );
}

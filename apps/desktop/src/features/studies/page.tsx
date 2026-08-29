import { Plus, BookOpen, Timer } from "lucide-react";

export function StudiesPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-50">Estudos</h1>
        <div className="flex gap-2">
          <button className="flex items-center gap-2 px-4 py-2 bg-surface-800 hover:bg-surface-700 text-surface-200 rounded-lg text-sm font-medium transition-colors border border-surface-700">
            <Timer className="w-4 h-4" />
            Cronômetro
          </button>
          <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
            <Plus className="w-4 h-4" />
            Nova matéria
          </button>
        </div>
      </div>

      {/* Empty state */}
      <div className="flex flex-col items-center justify-center py-20 text-center">
        <div className="p-4 rounded-full bg-surface-800/50 mb-4">
          <BookOpen className="w-10 h-10 text-surface-600" />
        </div>
        <h3 className="text-lg font-medium text-surface-300 mb-2">
          Nenhuma matéria cadastrada
        </h3>
        <p className="text-sm text-surface-500 mb-6 max-w-sm">
          Cadastre suas matérias e comece a registrar suas sessões de estudo.
        </p>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Cadastrar matéria
        </button>
      </div>
    </div>
  );
}

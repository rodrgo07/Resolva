import { Plus, Wallet, TrendingUp, TrendingDown } from "lucide-react";

export function FinancesPage() {
  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-surface-50">Finanças</h1>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Novo lançamento
        </button>
      </div>

      {/* Finance Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-4 h-4 text-green-400" />
            <span className="text-sm text-surface-400">Total recebido</span>
          </div>
          <p className="text-2xl font-bold text-green-400">R$ 0,00</p>
        </div>
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <TrendingDown className="w-4 h-4 text-red-400" />
            <span className="text-sm text-surface-400">Total gasto</span>
          </div>
          <p className="text-2xl font-bold text-red-400">R$ 0,00</p>
        </div>
        <div className="glass-card p-5">
          <div className="flex items-center gap-2 mb-2">
            <Wallet className="w-4 h-4 text-accent-400" />
            <span className="text-sm text-surface-400">Saldo</span>
          </div>
          <p className="text-2xl font-bold text-accent-400">R$ 0,00</p>
        </div>
      </div>

      {/* Empty state */}
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="p-4 rounded-full bg-surface-800/50 mb-4">
          <Wallet className="w-10 h-10 text-surface-600" />
        </div>
        <h3 className="text-lg font-medium text-surface-300 mb-2">
          Nenhum lançamento registrado
        </h3>
        <p className="text-sm text-surface-500 mb-6 max-w-sm">
          Comece registrando suas receitas e despesas para ter controle financeiro.
        </p>
        <button className="flex items-center gap-2 px-4 py-2 bg-accent-600 hover:bg-accent-700 text-white rounded-lg text-sm font-medium transition-colors">
          <Plus className="w-4 h-4" />
          Registrar lançamento
        </button>
      </div>
    </div>
  );
}

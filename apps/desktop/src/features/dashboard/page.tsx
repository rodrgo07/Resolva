import { getGreeting } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import {
  CheckSquare,
  Wallet,
  BookOpen,
  Mail,
  TrendingUp,
  Clock,
  AlertTriangle,
  Sparkles,
} from "lucide-react";

function SummaryCard({
  icon: Icon,
  title,
  children,
  color,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
  color: string;
}) {
  return (
    <div className="glass-card p-5 hover:border-surface-600/30 transition-colors duration-200">
      <div className="flex items-center gap-3 mb-4">
        <div className={`p-2 rounded-lg ${color}`}>
          <Icon className="w-5 h-5" />
        </div>
        <h3 className="text-sm font-medium text-surface-300">{title}</h3>
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function StatLine({ label, value, sub }: { label: string; value: string | number; sub?: string }) {
  return (
    <div className="flex items-center justify-between">
      <span className="text-sm text-surface-400">{label}</span>
      <div className="text-right">
        <span className="text-sm font-semibold text-surface-100">{value}</span>
        {sub && <span className="text-xs text-surface-500 ml-1">{sub}</span>}
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { userName, setCurrentPage } = useAppStore();
  const { greeting } = getGreeting();

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-surface-50">
          {greeting}, <span className="text-accent-400">{userName}</span>.
        </h1>
        <p className="text-surface-400 mt-1">
          Aqui está o que merece sua atenção hoje.
        </p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <SummaryCard
          icon={CheckSquare}
          title="Tarefas"
          color="bg-accent-500/10 text-accent-400"
        >
          <StatLine label="Pendentes" value={0} />
          <StatLine label="Atrasadas" value={0} />
          <StatLine label="Concluídas hoje" value={0} />
        </SummaryCard>

        <SummaryCard
          icon={Wallet}
          title="Finanças"
          color="bg-green-500/10 text-green-400"
        >
          <StatLine label="Gastos da semana" value="R$ 0,00" />
          <StatLine label="Gastos do mês" value="R$ 0,00" />
          <StatLine label="Saldo" value="R$ 0,00" />
        </SummaryCard>

        <SummaryCard
          icon={BookOpen}
          title="Estudos"
          color="bg-blue-500/10 text-blue-400"
        >
          <StatLine label="Estudado hoje" value="0h 0min" />
          <StatLine label="Meta diária" value="2h" />
          <StatLine label="Progresso" value="0%" />
        </SummaryCard>

        <SummaryCard
          icon={Mail}
          title="Emails"
          color="bg-orange-500/10 text-orange-400"
        >
          <StatLine label="Não lidos" value={0} />
          <StatLine label="Importantes" value={0} />
          <StatLine label="Precisam resposta" value={0} />
        </SummaryCard>
      </div>

      {/* Resolva Recomenda */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-accent-400" />
          <h2 className="text-lg font-semibold text-surface-100">
            Resolva recomenda
          </h2>
        </div>
        <div className="space-y-3">
          <RecommendationCard
            icon={Clock}
            message="Comece cadastrando suas tarefas para acompanhar sua produtividade."
            action="Ir para Tarefas"
            onClick={() => setCurrentPage("tasks")}
          />
          <RecommendationCard
            icon={TrendingUp}
            message="Registre seus gastos para ter controle financeiro completo."
            action="Ir para Finanças"
            onClick={() => setCurrentPage("finances")}
          />
          <RecommendationCard
            icon={AlertTriangle}
            message="Configure suas matérias de estudo e defina metas semanais."
            action="Ir para Estudos"
            onClick={() => setCurrentPage("studies")}
          />
        </div>
      </div>
    </div>
  );
}

function RecommendationCard({
  icon: Icon,
  message,
  action,
  onClick,
}: {
  icon: React.ElementType;
  message: string;
  action: string;
  onClick: () => void;
}) {
  return (
    <div className="glass-card p-4 flex items-center gap-4 hover:border-accent-500/20 transition-colors duration-200">
      <Icon className="w-5 h-5 text-accent-400 shrink-0" />
      <p className="text-sm text-surface-300 flex-1">{message}</p>
      <button
        onClick={onClick}
        className="text-sm text-accent-400 hover:text-accent-300 font-medium whitespace-nowrap transition-colors"
      >
        {action} →
      </button>
    </div>
  );
}

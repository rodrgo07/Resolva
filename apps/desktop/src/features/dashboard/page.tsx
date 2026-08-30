import { useEffect, useState } from "react";
import { getGreeting, formatCurrency } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import { api } from "@/lib/api-client";
import {
  CheckSquare,
  Wallet,
  BookOpen,
  Mail,
  TrendingUp,
  AlertTriangle,
  Sparkles,
  CalendarDays,
  Flame,
  ArrowRight
} from "lucide-react";
import { Button } from "@/components/ui/button";

interface TasksSummary {
  total: number;
  pending: number;
  completed: number;
  overdue: number;
}

interface FinancesSummary {
  total_income: number;
  total_expense: number;
  balance: number;
}

interface StudiesSummary {
  hours_today: number;
  hours_this_week: number;
  hours_this_month: number;
  by_subject?: unknown[];
}

interface EmailsSummary {
  unread_count: number;
  important_count: number;
  needs_reply_count: number;
}

function SummaryCard({
  icon: Icon,
  title,
  children,
  color,
  onClick,
}: {
  icon: React.ElementType;
  title: string;
  children: React.ReactNode;
  color: string;
  onClick?: () => void;
}) {
  return (
    <div 
      onClick={onClick}
      className="glass-card p-5 hover:border-surface-600/50 hover:bg-surface-900/80 transition-all duration-200 cursor-pointer flex flex-col justify-between group"
    >
      <div>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${color}`}>
              <Icon className="w-5 h-5" />
            </div>
            <h3 className="text-sm font-semibold text-surface-200 group-hover:text-white transition-colors">{title}</h3>
          </div>
          <ArrowRight className="w-4 h-4 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
        </div>
        <div className="space-y-2">{children}</div>
      </div>
    </div>
  );
}

function StatLine({ label, value, sub, highlight }: { label: string; value: string | number; sub?: string; highlight?: boolean }) {
  return (
    <div className="flex items-center justify-between py-0.5">
      <span className="text-xs text-surface-400">{label}</span>
      <div className="text-right">
        <span className={`text-xs font-semibold ${highlight ? "text-red-400 font-bold" : "text-surface-100"}`}>
          {value}
        </span>
        {sub && <span className="text-[10px] text-surface-500 ml-1">{sub}</span>}
      </div>
    </div>
  );
}

export function DashboardPage() {
  const { userName, setCurrentPage } = useAppStore();
  const { greeting } = getGreeting();

  const [tasksSummary, setTasksSummary] = useState<TasksSummary>({ total: 0, pending: 0, completed: 0, overdue: 0 });
  const [financesSummary, setFinancesSummary] = useState<FinancesSummary>({ total_income: 0, total_expense: 0, balance: 0 });
  const [studiesSummary, setStudiesSummary] = useState<StudiesSummary>({ hours_today: 0, hours_this_week: 0, hours_this_month: 0 });
  const [emailsSummary, setEmailsSummary] = useState<EmailsSummary>({ unread_count: 0, important_count: 0, needs_reply_count: 0 });

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [tasks, finances, studies, emails] = await Promise.allSettled([
          api.get<TasksSummary>("/api/tasks/summary"),
          api.get<FinancesSummary>("/api/finances/summary"),
          api.get<StudiesSummary>("/api/studies/summary"),
          api.get<EmailsSummary>("/api/emails/summary"),
        ]);

        if (tasks.status === "fulfilled") setTasksSummary(tasks.value);
        if (finances.status === "fulfilled") setFinancesSummary(finances.value);
        if (studies.status === "fulfilled") setStudiesSummary(studies.value);
        if (emails.status === "fulfilled") setEmailsSummary(emails.value);
      } catch (err) {
        console.error("Erro ao carregar dados do dashboard:", err);
      }
    }

    loadDashboardData();
  }, []);

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Greeting Header & Agent Callout */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-surface-800/40 pb-6">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">
            {greeting}, <span className="text-accent-400">{userName}</span>.
          </h1>
          <p className="text-surface-400 mt-1 text-sm">
            Aqui está o panorama completo da sua rotina hoje.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Button
            size="sm"
            onClick={() => setCurrentPage("ai")}
            className="gap-2 bg-accent-600 hover:bg-accent-500 shadow-md shadow-accent-600/20 text-xs font-bold"
          >
            <Sparkles className="w-3.5 h-3.5" />
            Organizar Meu Dia com Agent
          </Button>
          <div className="flex items-center gap-2 text-xs font-medium text-surface-400 glass px-3 py-1.5 rounded-lg border border-surface-700/50 hidden md:flex">
            <CalendarDays className="w-4 h-4 text-accent-400" />
            <span>{new Intl.DateTimeFormat("pt-BR", { dateStyle: "full" }).format(new Date())}</span>
          </div>
        </div>
      </div>

      {/* Summary Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        <SummaryCard
          icon={CheckSquare}
          title="Tarefas"
          color="bg-accent-500/10 text-accent-400"
          onClick={() => setCurrentPage("tasks")}
        >
          <StatLine label="Pendentes" value={tasksSummary.pending} />
          <StatLine label="Atrasadas" value={tasksSummary.overdue} highlight={tasksSummary.overdue > 0} />
          <StatLine label="Concluídas" value={tasksSummary.completed} />
        </SummaryCard>

        <SummaryCard
          icon={Wallet}
          title="Finanças"
          color="bg-green-500/10 text-green-400"
          onClick={() => setCurrentPage("finances")}
        >
          <StatLine label="Receitas" value={formatCurrency(financesSummary.total_income)} />
          <StatLine label="Despesas" value={formatCurrency(financesSummary.total_expense)} />
          <StatLine label="Saldo Atual" value={formatCurrency(financesSummary.balance)} />
        </SummaryCard>

        <SummaryCard
          icon={BookOpen}
          title="Estudos"
          color="bg-blue-500/10 text-blue-400"
          onClick={() => setCurrentPage("studies")}
        >
          <StatLine label="Hoje" value={`${studiesSummary.hours_today.toFixed(1)}h`} />
          <StatLine label="Esta Semana" value={`${studiesSummary.hours_this_week.toFixed(1)}h`} />
          <StatLine label="Este Mês" value={`${studiesSummary.hours_this_month.toFixed(1)}h`} />
        </SummaryCard>

        <SummaryCard
          icon={Mail}
          title="Emails (Gmail + Outlook)"
          color="bg-orange-500/10 text-orange-400"
          onClick={() => setCurrentPage("emails")}
        >
          <StatLine label="Não lidos" value={emailsSummary.unread_count} />
          <StatLine label="Importantes" value={emailsSummary.important_count} />
          <StatLine label="Precisam de resposta" value={emailsSummary.needs_reply_count} highlight={emailsSummary.needs_reply_count > 0} />
        </SummaryCard>
      </div>

      {/* Resolva Recomenda — Recomendações Dinâmicas */}
      <div>
        <div className="flex items-center gap-2 mb-4">
          <Sparkles className="w-5 h-5 text-accent-400" />
          <h2 className="text-lg font-bold text-white tracking-tight">
            Resolva recomenda
          </h2>
        </div>

        <div className="space-y-3">
          {tasksSummary.overdue > 0 && (
            <RecommendationCard
              icon={AlertTriangle}
              color="text-red-400 bg-red-500/10 border-red-500/20"
              message={`Você possui ${tasksSummary.overdue} tarefa(s) com prazo atrasado que exigem atenção imediata.`}
              action="Ver Tarefas Atrasadas"
              onClick={() => setCurrentPage("tasks")}
            />
          )}

          {tasksSummary.pending > 0 && tasksSummary.overdue === 0 && (
            <RecommendationCard
              icon={CheckSquare}
              color="text-accent-400 bg-accent-500/10 border-accent-500/20"
              message={`Você tem ${tasksSummary.pending} tarefa(s) pendentes para concluir hoje.`}
              action="Ver Tarefas"
              onClick={() => setCurrentPage("tasks")}
            />
          )}

          {studiesSummary.hours_this_week < 5 && (
            <RecommendationCard
              icon={Flame}
              color="text-yellow-400 bg-yellow-500/10 border-yellow-500/20"
              message={`Você acumulou ${studiesSummary.hours_this_week.toFixed(1)}h de estudo nesta semana. Inicie um Pomodoro para avançar na sua meta!`}
              action="Estudar Agora"
              onClick={() => setCurrentPage("studies")}
            />
          )}

          {financesSummary.total_expense > 0 && (
            <RecommendationCard
              icon={TrendingUp}
              color="text-green-400 bg-green-500/10 border-green-500/20"
              message={`Seu saldo atual é de ${formatCurrency(financesSummary.balance)}. Mantenha o acompanhamento dos orçamentos mensais.`}
              action="Ver Finanças"
              onClick={() => setCurrentPage("finances")}
            />
          )}

          {emailsSummary.needs_reply_count > 0 && (
            <RecommendationCard
              icon={Mail}
              color="text-orange-400 bg-orange-500/10 border-orange-500/20"
              message={`Existem ${emailsSummary.needs_reply_count} email(s) classificados como prioritários aguardando resposta.`}
              action="Revisar Emails"
              onClick={() => setCurrentPage("emails")}
            />
          )}
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
  color = "text-accent-400 bg-accent-500/10 border-accent-500/20",
}: {
  icon: React.ElementType;
  message: string;
  action: string;
  onClick: () => void;
  color?: string;
}) {
  return (
    <div className="glass-card p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:border-surface-600 transition-colors duration-200">
      <div className="flex items-center gap-3">
        <div className={`p-2 rounded-lg shrink-0 border ${color}`}>
          <Icon className="w-4 h-4" />
        </div>
        <p className="text-sm text-surface-200 leading-snug">{message}</p>
      </div>
      <button
        onClick={onClick}
        className="text-xs font-semibold text-accent-400 hover:text-accent-300 transition-colors whitespace-nowrap self-end sm:self-center cursor-pointer flex items-center gap-1"
      >
        <span>{action}</span>
        <ArrowRight className="w-3.5 h-3.5" />
      </button>
    </div>
  );
}

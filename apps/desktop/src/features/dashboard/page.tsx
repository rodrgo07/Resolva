import { useEffect, useState } from "react";
import { getGreeting } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import { api } from "@/lib/api-client";
import {
  CheckSquare, Wallet, BookOpen, Mail, 
  AlertTriangle, Sparkles, CalendarDays, 
  ArrowRight, Play, Clock, Zap, RefreshCw,
  ChevronRight
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { LoadingState } from "@/components/shared/loading-state";

interface DashboardOverview {
  current_time: string;
  today_date: string;
  tasks: {
    total: number;
    pending: number;
    overdue: number;
    completed: number;
  };
  calendar: {
    events_today_count: number;
    next_event: {
      id: number;
      title: string;
      start_time: string;
      start_date: string;
    } | null;
  };
  emails: {
    unread_count: number;
    critical_count: number;
    important_count: number;
  };
  studies: {
    minutes_today: number;
    hours_today: number;
    hours_week: number;
  };
  finances: {
    expense_today: number;
    expense_week: number;
  };
  automations: {
    active_count: number;
  };
}

interface NowCardData {
  type: string;
  badge: string;
  title: string;
  description: string;
  action_label: string;
  action_target: "tasks" | "emails" | "calendar" | "studies" | "finances" | "ai" | "automations";
  priority_level: "critical" | "high" | "medium" | "normal" | "low";
}

interface TimelineItem {
  time: string;
  category: string;
  title: string;
  description: string;
  icon: string;
}

interface RecommendationItem {
  id: string;
  type: string;
  title: string;
  message: string;
  action: string;
  target: "tasks" | "emails" | "calendar" | "studies" | "finances" | "ai" | "automations";
  variant: "destructive" | "warning" | "info" | "secondary";
}

export function DashboardPage() {
  const { userName, setCurrentPage } = useAppStore();
  const { greeting } = getGreeting();

  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [nowCard, setNowCard] = useState<NowCardData | null>(null);
  const [timeline, setTimeline] = useState<TimelineItem[]>([]);
  const [recommendations, setRecommendations] = useState<RecommendationItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [hasError, setHasError] = useState(false);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      setHasError(false);

      const [ovRes, nowRes, tlRes, recRes] = await Promise.allSettled([
        api.get<DashboardOverview>("/api/dashboard/overview"),
        api.get<NowCardData>("/api/dashboard/now"),
        api.get<TimelineItem[]>("/api/dashboard/timeline"),
        api.get<RecommendationItem[]>("/api/dashboard/recommendations"),
      ]);

      if (ovRes.status === "fulfilled") setOverview(ovRes.value);
      if (nowRes.status === "fulfilled") setNowCard(nowRes.value);
      if (tlRes.status === "fulfilled") setTimeline(tlRes.value || []);
      if (recRes.status === "fulfilled") setRecommendations(recRes.value || []);
    } catch {
      setHasError(true);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  if (isLoading) {
    return <LoadingState message="Carregando sua Central de Comando Inteligente..." />;
  }

  if (hasError || !overview) {
    return (
      <div className="flex flex-col items-center justify-center py-20 text-center glass-card">
        <AlertTriangle className="w-10 h-10 text-red-400 mb-3" />
        <h3 className="text-base font-bold text-white mb-1">Não foi possível carregar os dados operacionais</h3>
        <p className="text-xs text-surface-400 mb-4">Verifique se o backend do Resolva está em execução.</p>
        <Button onClick={loadDashboardData} size="sm" className="gap-2">
          <RefreshCw className="w-3.5 h-3.5" />
          Tentar Novamente
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in pb-8">
      {/* 1. Header / Saudação Contextual */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-[11px] font-semibold text-emerald-400 uppercase tracking-wider">
              Central de Comando Ativa
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight mt-0.5">
            {greeting}, <span className="text-accent-400">{userName}</span>.
          </h1>
          <p className="text-surface-400 text-xs mt-1">
            Aqui está o que merece sua atenção exatamente agora.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <Button
            onClick={() => setCurrentPage("ai")}
            className="gap-2 bg-accent-600 hover:bg-accent-500 shadow-lg shadow-accent-600/25 font-bold text-xs"
          >
            <Sparkles className="w-4 h-4" />
            Organizar Meu Dia
          </Button>

          <div className="flex items-center gap-2 text-xs font-medium text-surface-400 glass px-3 py-1.5 rounded-lg border border-surface-700/50 hidden md:flex">
            <CalendarDays className="w-3.5 h-3.5 text-accent-400" />
            <span>{new Intl.DateTimeFormat("pt-BR", { dateStyle: "full" }).format(new Date())}</span>
          </div>
        </div>
      </div>

      {/* 2. Card "AGORA" — Foco Imediato */}
      {nowCard && (
        <div className="glass-card p-5 border-l-4 border-l-accent-500 bg-gradient-to-r from-accent-600/10 via-surface-900/40 to-surface-900/20 flex flex-col sm:flex-row sm:items-center justify-between gap-4 shadow-xl">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <Badge variant="default" className="text-[10px] uppercase font-mono tracking-wider bg-accent-500/20 text-accent-300 border border-accent-500/40">
                {nowCard.badge}
              </Badge>
              <span className="text-[11px] text-surface-400">Recomendação do Resolva Agent</span>
            </div>
            <h2 className="text-xl font-bold text-white tracking-tight">{nowCard.title}</h2>
            <p className="text-xs text-surface-300 max-w-xl">{nowCard.description}</p>
          </div>

          <Button
            size="sm"
            onClick={() => setCurrentPage(nowCard.action_target)}
            className="gap-1.5 font-bold shrink-0 self-start sm:self-center shadow-md shadow-accent-600/20"
          >
            <span>{nowCard.action_label}</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </Button>
        </div>
      )}

      {/* 3. Resumo Operacional do Dia ("Seu Dia") */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {/* Tarefas */}
        <div 
          onClick={() => setCurrentPage("tasks")}
          className="glass-card p-4 hover:border-surface-600 transition-all cursor-pointer flex flex-col justify-between group space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-accent-500/10 text-accent-400">
                <CheckSquare className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Tarefas</h3>
            </div>
            <ChevronRight className="w-4 h-4 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-surface-300">
              <span>Pendentes:</span>
              <span className="font-bold text-white">{overview.tasks.pending}</span>
            </div>
            <div className="flex justify-between text-surface-300">
              <span>Atrasadas:</span>
              <span className={`font-bold ${overview.tasks.overdue > 0 ? "text-red-400" : "text-surface-400"}`}>
                {overview.tasks.overdue}
              </span>
            </div>
            <div className="flex justify-between text-surface-300">
              <span>Concluídas:</span>
              <span className="font-bold text-emerald-400">{overview.tasks.completed}</span>
            </div>
          </div>
        </div>

        {/* Agenda */}
        <div 
          onClick={() => setCurrentPage("calendar")}
          className="glass-card p-4 hover:border-surface-600 transition-all cursor-pointer flex flex-col justify-between group space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
                <CalendarDays className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Agenda</h3>
            </div>
            <ChevronRight className="w-4 h-4 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-surface-300">
              <span>Eventos hoje:</span>
              <span className="font-bold text-white">{overview.calendar.events_today_count}</span>
            </div>
            <div className="text-[11px] text-surface-400 truncate pt-1">
              Próximo: <strong className="text-surface-200">{overview.calendar.next_event?.title || "Nenhum"}</strong>
            </div>
          </div>
        </div>

        {/* E-mails */}
        <div 
          onClick={() => setCurrentPage("emails")}
          className="glass-card p-4 hover:border-surface-600 transition-all cursor-pointer flex flex-col justify-between group space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-orange-500/10 text-orange-400">
                <Mail className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white">E-mails</h3>
            </div>
            <ChevronRight className="w-4 h-4 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-surface-300">
              <span>Não lidos:</span>
              <span className="font-bold text-white">{overview.emails.unread_count}</span>
            </div>
            <div className="flex justify-between text-surface-300">
              <span>Urgentes / Críticos:</span>
              <span className={`font-bold ${overview.emails.critical_count > 0 ? "text-red-400" : "text-surface-400"}`}>
                {overview.emails.critical_count}
              </span>
            </div>
          </div>
        </div>

        {/* Estudos & Finanças */}
        <div 
          onClick={() => setCurrentPage("studies")}
          className="glass-card p-4 hover:border-surface-600 transition-all cursor-pointer flex flex-col justify-between group space-y-3"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
                <BookOpen className="w-4 h-4" />
              </div>
              <h3 className="text-sm font-bold text-white">Estudos & Metas</h3>
            </div>
            <ChevronRight className="w-4 h-4 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between text-surface-300">
              <span>Estudado hoje:</span>
              <span className="font-bold text-white">{overview.studies.hours_today}h</span>
            </div>
            <div className="flex justify-between text-surface-300">
              <span>Esta semana:</span>
              <span className="font-bold text-accent-400">{overview.studies.hours_week}h</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Timeline do Dia + Ações Rápidas Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Timeline */}
        <div className="lg:col-span-2 glass-card p-5 space-y-4">
          <div className="flex items-center justify-between border-b border-surface-800 pb-3">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Clock className="w-4 h-4 text-accent-400" />
              Timeline & Fluxo do Dia
            </h3>
            <span className="text-[11px] text-surface-400">Ordem cronológica</span>
          </div>

          <div className="space-y-3 max-h-[360px] overflow-y-auto pr-2">
            {timeline.map((item, idx) => (
              <div key={idx} className="flex items-start gap-3 p-2.5 rounded-lg bg-surface-900/60 border border-surface-800/80 text-xs">
                <div className="px-2 py-1 rounded bg-surface-800 font-mono text-[11px] font-bold text-accent-400 whitespace-nowrap">
                  {item.time}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-semibold text-white truncate">{item.title}</h4>
                  <p className="text-surface-400 text-[11px] truncate">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions Shortcuts */}
        <div className="glass-card p-5 space-y-3">
          <h3 className="text-sm font-bold text-white flex items-center gap-2 border-b border-surface-800 pb-3">
            <Zap className="w-4 h-4 text-yellow-400" />
            Ações Rápidas
          </h3>

          <div className="space-y-2">
            {[
              { label: "+ Nova Tarefa", target: "tasks" as const, icon: CheckSquare },
              { label: "+ Registrar Gasto", target: "finances" as const, icon: Wallet },
              { label: "+ Novo Compromisso", target: "calendar" as const, icon: CalendarDays },
              { label: "Iniciar Pomodoro", target: "studies" as const, icon: Play },
              { label: "Ver E-mails (Gmail & Outlook)", target: "emails" as const, icon: Mail },
              { label: "Rotinas & Automações", target: "automations" as const, icon: Zap },
              { label: "Perguntar ao Agent", target: "ai" as const, icon: Sparkles },
            ].map((btn, i) => {
              const Icon = btn.icon;
              return (
                <button
                  key={i}
                  onClick={() => setCurrentPage(btn.target)}
                  className="w-full flex items-center justify-between p-2.5 rounded-lg border border-surface-800 bg-surface-900/40 hover:bg-surface-800/80 hover:border-accent-500/30 text-xs font-medium text-surface-200 transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-2">
                    <Icon className="w-3.5 h-3.5 text-accent-400" />
                    <span>{btn.label}</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-surface-500 opacity-0 group-hover:opacity-100 transition-opacity" />
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* 5. Resolva Recomenda — Recomendações Dinâmicas */}
      {recommendations.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-accent-400" />
            <h2 className="text-base font-bold text-white tracking-tight">
              Resolva Recomenda
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {recommendations.map((rec) => (
              <div
                key={rec.id}
                className="glass-card p-4 flex items-center justify-between gap-3 hover:border-surface-600 transition-colors"
              >
                <div className="space-y-0.5 min-w-0">
                  <h4 className="text-xs font-bold text-white truncate">{rec.title}</h4>
                  <p className="text-[11px] text-surface-400 line-clamp-1">{rec.message}</p>
                </div>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setCurrentPage(rec.target)}
                  className="text-xs h-7 gap-1 border-surface-700 hover:text-white shrink-0"
                >
                  <span>{rec.action}</span>
                  <ChevronRight className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

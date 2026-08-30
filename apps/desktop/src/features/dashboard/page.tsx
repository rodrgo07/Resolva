import { useEffect, useState } from "react";
import { getGreeting } from "@/lib/utils";
import { useAppStore } from "@/stores/app-store";
import { api } from "@/lib/api-client";
import {
  CheckSquare, Wallet, BookOpen, Mail, 
  AlertTriangle, Sparkles, CalendarDays, 
  ArrowRight, Play, Zap, RefreshCw,
  ChevronRight, Compass, ShieldCheck, Flame, Layers
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

export function DashboardPage() {
  const { setCurrentPage } = useAppStore();
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const fetchOverview = async (showLoading = true) => {
    if (showLoading) setIsLoading(true);

    try {
      const data = await api.get<DashboardOverview>("/api/dashboard/overview");
      setOverview(data);
    } catch (err) {
      console.error("Erro ao carregar dashboard:", err);
    } finally {
      setIsLoading(false);
    }
  };


  useEffect(() => {
    fetchOverview();
  }, []);

  if (isLoading) {
    return <LoadingState message="Sincronizando com o centro de inteligência..." />;
  }

  if (!overview) {
    return (
      <div className="flex flex-col items-center justify-center p-12 text-center space-y-4 glass-card rounded-2xl max-w-lg mx-auto mt-12 animate-fade-in border border-border">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-warning shadow-md">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-xl font-bold text-text-primary">Backend Offline</h2>
        <p className="text-sm text-text-secondary max-w-md leading-relaxed">
          Não foi possível sincronizar seus dados locais com o núcleo do Resolva. O aplicativo continuará tentando reconectar automaticamente.
        </p>
        <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-surface-elevated border border-border text-[11px] text-text-muted">
          <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
          <span>API: 127.0.0.1:8700</span>
        </div>
        <Button onClick={() => fetchOverview(true)} className="gap-2 mt-2 shadow-lg shadow-accent/20">
          <RefreshCw className="w-4 h-4" /> Tentar Novamente
        </Button>
      </div>
    );
  }


  return (
    <div className="space-y-8 animate-fade-in pb-12 max-w-7xl mx-auto">
      {/* 1. Header Hero Premium com Saudação Dinâmica e Focus Score */}
      <div className="glass-card p-6 md:p-8 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-purple-500/10 via-accent/5 to-transparent rounded-full blur-3xl -z-10 pointer-events-none" />
        
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <Badge variant="outline" className="text-xs bg-accent/10 border-accent/30 text-accent-light px-3 py-1 gap-1.5 rounded-full">
              <Sparkles className="w-3.5 h-3.5" /> Resolva AI Core Ativo
            </Badge>
            <span className="text-xs text-text-muted">{overview.today_date} • {overview.current_time}</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold tracking-tight text-text-primary">
            {getGreeting().greeting}, <span className="text-transparent bg-clip-text bg-gradient-to-r from-accent to-accent-light">Rodrigo</span>
          </h1>

          <p className="text-sm text-text-secondary max-w-xl">
            Seu assistente inteligente já priorizou suas tarefas e alinhou seus compromissos para garantir máximo foco hoje.
          </p>
        </div>

        {/* Focus Score Indicator */}
        <div className="flex items-center gap-4 p-4 rounded-xl bg-surface-elevated/80 border border-border shrink-0 shadow-lg">
          <div className="relative flex items-center justify-center w-14 h-14 rounded-full bg-accent/20 border-2 border-accent">
            <Flame className="w-7 h-7 text-accent-light animate-pulse" />
          </div>
          <div>
            <div className="text-xs font-semibold text-text-muted uppercase tracking-wider">Focus Score</div>
            <div className="text-2xl font-black text-text-primary">88%</div>
            <div className="text-[11px] text-success font-medium">Fluxo de Alta Performance</div>
          </div>
        </div>
      </div>

      {/* 2. Card Prioritário "AGORA" (Ação Recomendada pela IA) */}
      <div className="glass-card p-6 rounded-2xl border-l-4 border-l-accent relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-accent text-text-primary">AGORA</span>
              <span className="text-xs font-semibold text-accent-light">Recomendação Prioritária do Agent</span>
            </div>
            <h2 className="text-lg font-bold text-text-primary">
              {overview.calendar.next_event 
                ? `Preparar para: ${overview.calendar.next_event.title}` 
                : (overview.tasks.pending > 0 ? "Revisar e avançar nas tarefas pendentes do dia" : "Planejamento e alinhamento de novos projetos")}
            </h2>
            <p className="text-xs text-text-secondary">
              {overview.calendar.next_event
                ? `Seu próximo evento começa às ${overview.calendar.next_event.start_time}. A IA preparou o briefing de contexto.`
                : "Nenhum compromisso imediato em conflito. Momento ideal para um bloco de foco ininterrupto."}
            </p>
          </div>


          <div className="flex items-center gap-3 shrink-0">
            <Button onClick={() => setCurrentPage("studies")} className="gap-2 shadow-lg shadow-accent/20">
              <Play className="w-4 h-4" /> Iniciar Bloco de Foco
            </Button>
            <Button variant="outline" onClick={() => setCurrentPage("ai")} className="gap-2">
              <Sparkles className="w-4 h-4 text-accent-light" /> Consultar Agent
            </Button>
          </div>
        </div>
      </div>

      {/* 3. Grid de Cards de Resumo dos Módulos */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        {/* Tarefas */}
        <div 
          onClick={() => setCurrentPage("tasks")}
          className="glass-card p-5 rounded-xl cursor-pointer hover:border-accent/40 transition-all flex flex-col justify-between space-y-4 group"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-blue-500/10 text-info border border-blue-500/20">
                <CheckSquare className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-text-primary">Tarefas</h3>
                <span className="text-[11px] text-text-muted">{overview.tasks.total} registradas</span>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
          </div>
          <div className="space-y-1 text-xs border-t border-border pt-3">
            <div className="flex justify-between text-text-secondary">
              <span>Pendentes:</span>
              <span className="font-bold text-text-primary">{overview.tasks.pending}</span>
            </div>
            <div className="flex justify-between text-text-secondary">
              <span>Atrasadas:</span>
              <span className={`font-bold ${overview.tasks.overdue > 0 ? "text-error" : "text-success"}`}>
                {overview.tasks.overdue}
              </span>
            </div>
          </div>
        </div>

        {/* Calendário */}
        <div 
          onClick={() => setCurrentPage("calendar")}
          className="glass-card p-5 rounded-xl cursor-pointer hover:border-accent/40 transition-all flex flex-col justify-between space-y-4 group"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-accent/10 text-accent-light border border-accent/20">
                <CalendarDays className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-text-primary">Agenda</h3>
                <span className="text-[11px] text-text-muted">{overview.calendar.events_today_count} hoje</span>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
          </div>
          <div className="space-y-1 text-xs border-t border-border pt-3">
            <div className="text-[11px] text-text-secondary truncate">
              Próximo: <strong className="text-text-primary">{overview.calendar.next_event?.title || "Nenhum compromisso"}</strong>
            </div>
            <div className="text-[11px] text-text-muted">
              {overview.calendar.next_event ? `Horário: ${overview.calendar.next_event.start_time}` : "Dia livre de reuniões"}
            </div>
          </div>
        </div>

        {/* E-mails */}
        <div 
          onClick={() => setCurrentPage("emails")}
          className="glass-card p-5 rounded-xl cursor-pointer hover:border-accent/40 transition-all flex flex-col justify-between space-y-4 group"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-orange-500/10 text-orange-400 border border-orange-500/20">
                <Mail className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-text-primary">E-mails</h3>
                <span className="text-[11px] text-text-muted">Gmail & Outlook</span>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
          </div>
          <div className="space-y-1 text-xs border-t border-border pt-3">
            <div className="flex justify-between text-text-secondary">
              <span>Não lidos:</span>
              <span className="font-bold text-text-primary">{overview.emails.unread_count}</span>
            </div>
            <div className="flex justify-between text-text-secondary">
              <span>Importantes / Urgentes:</span>
              <span className={`font-bold ${overview.emails.critical_count > 0 ? "text-error" : "text-success"}`}>
                {overview.emails.critical_count}
              </span>
            </div>

          </div>
        </div>

        {/* Automações & Workflows */}
        <div 
          onClick={() => setCurrentPage("automations")}
          className="glass-card p-5 rounded-xl cursor-pointer hover:border-accent/40 transition-all flex flex-col justify-between space-y-4 group"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2.5 rounded-lg bg-emerald-500/10 text-success border border-emerald-500/20">
                <Zap className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-text-primary">Automações</h3>
                <span className="text-[11px] text-text-muted">{overview.automations.active_count} ativas</span>
              </div>
            </div>
            <ChevronRight className="w-4 h-4 text-text-muted group-hover:text-accent-light group-hover:translate-x-0.5 transition-all" />
          </div>
          <div className="space-y-1 text-xs border-t border-border pt-3">
            <div className="flex justify-between text-text-secondary">
              <span>Rotinas ativas:</span>
              <span className="font-bold text-success">{overview.automations.active_count}</span>
            </div>
            <div className="flex justify-between text-text-secondary">
              <span>Modo:</span>
              <span className="font-bold text-accent-light">Orquestração Adaptativa</span>
            </div>
          </div>
        </div>
      </div>

      {/* 4. Seção Inferior: Ações Rápidas & Insights do Agent */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Painel de Ações Rápidas */}
        <div className="glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center gap-2 border-b border-border pb-3">
            <Zap className="w-4 h-4 text-warning" />
            <h3 className="text-sm font-bold text-text-primary">Ações Imediatas</h3>
          </div>

          <div className="space-y-2">
            {[
              { label: "Nova Tarefa Prioritária", target: "tasks" as const, icon: CheckSquare },
              { label: "Novo Compromisso na Agenda", target: "calendar" as const, icon: CalendarDays },
              { label: "Iniciar Sessão de Estudos / Pomodoro", target: "studies" as const, icon: BookOpen },
              { label: "Registrar Transação Financeira", target: "finances" as const, icon: Wallet },
              { label: "Executar Orquestração de Rotinas", target: "automations" as const, icon: Layers },
            ].map((act, i) => {
              const Icon = act.icon;
              return (
                <button
                  key={i}
                  onClick={() => setCurrentPage(act.target)}
                  className="w-full flex items-center justify-between p-3 rounded-xl border border-border bg-surface-elevated/40 hover:bg-surface-hover hover:border-accent/30 text-xs font-medium text-text-secondary hover:text-text-primary transition-all cursor-pointer group"
                >
                  <div className="flex items-center gap-2.5">
                    <Icon className="w-4 h-4 text-accent-light" />
                    <span>{act.label}</span>
                  </div>
                  <ArrowRight className="w-3.5 h-3.5 text-text-muted group-hover:text-text-primary group-hover:translate-x-0.5 transition-all" />
                </button>
              );
            })}
          </div>
        </div>

        {/* Painel do Agent Insight */}
        <div className="lg:col-span-2 glass-card p-6 rounded-2xl space-y-4">
          <div className="flex items-center justify-between border-b border-border pb-3">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-accent-light" />
              <h3 className="text-sm font-bold text-text-primary">Insights & Análise Preditiva do Agent</h3>
            </div>
            <Badge variant="outline" className="text-[10px] bg-accent/10 border-accent/30 text-accent-light">
              Fase 35 Hardened
            </Badge>
          </div>

          <div className="space-y-3">
            <div className="p-4 rounded-xl bg-surface-elevated/60 border border-border text-xs space-y-1">
              <div className="font-semibold text-text-primary flex items-center gap-2">
                <ShieldCheck className="w-4 h-4 text-success" />
                Permission Layer & Autonomia Segura
              </div>
              <p className="text-text-secondary leading-relaxed">
                Todas as automações e comandos remotos mobile estão operando sob a Permission Layer estrita do backend, garantindo proteção total contra execução não homologada.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-surface-elevated/60 border border-border text-xs space-y-1">
              <div className="font-semibold text-text-primary flex items-center gap-2">
                <Compass className="w-4 h-4 text-accent-light" />
                Planejamento Semanal
              </div>
              <p className="text-text-secondary leading-relaxed">
                Você completou 85% das metas previstas para a semana. Continue mantendo a cadência de estudos e revisão de notificações diárias.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

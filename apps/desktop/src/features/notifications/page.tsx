import { useState, useEffect, useMemo } from "react";
import { 
  Bell, CheckCheck, CheckCircle2, Wallet, BookOpen, ArrowRight, 
  CalendarDays, Mail, Sparkles, RefreshCw, X, AlertTriangle, ShieldCheck
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";
import { useNotificationStore } from "@/stores/notification-store";
import { useAppStore } from "@/stores/app-store";
import { formatDate } from "@/lib/utils";
import type { Notification } from "@/types";

export function NotificationsPage() {
  const { 
    notifications, setNotifications, markAsRead, markAllAsRead, 
    dismissNotification, summary, fetchSummary 
  } = useNotificationStore();
  const { setCurrentPage } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState<
    "all" | "unread" | "urgent" | "tasks" | "calendar" | "emails" | "studies" | "finances" | "agent"
  >("all");
  const { toast } = useToast();

  const loadNotifications = async () => {
    try {
      setIsLoading(true);
      const [notifsData] = await Promise.all([
        api.get<Notification[]>("/api/notifications/"),
        fetchSummary()
      ]);
      setNotifications(notifsData || []);
    } catch {
      toast({ title: "Erro ao carregar notificações", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadNotifications();
  }, []);

  const handleMarkAsRead = async (id: number) => {
    try {
      await api.post(`/api/notifications/${id}/read`, {});
      markAsRead(id);
      fetchSummary();
      toast({ title: "Notificação marcada como lida", type: "info" });
    } catch {
      toast({ title: "Erro ao atualizar notificação", type: "error" });
    }
  };

  const handleDismiss = async (id: number) => {
    try {
      await api.post(`/api/notifications/${id}/dismiss`, {});
      dismissNotification(id);
      fetchSummary();
      toast({ title: "Notificação dispensada", type: "info" });
    } catch {
      toast({ title: "Erro ao dispensar", type: "error" });
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.post("/api/notifications/read-all", {});
      markAllAsRead();
      fetchSummary();
      toast({ title: "Todas as notificações foram marcadas como lidas", type: "success" });
    } catch {
      toast({ title: "Erro ao marcar todas como lidas", type: "error" });
    }
  };

  const handleExecuteAction = async (notif: Notification) => {
    if (!notif.action_type) return;
    try {
      const res = await api.post<{ success: boolean; message?: string }>(`/api/notifications/${notif.id}/action`, {
        confirmed: true
      });
      if (res?.success) {
        toast({ title: "Ação executada", description: res.message || "Ação concluída.", type: "success" });
        markAsRead(notif.id);
        fetchSummary();
      }
    } catch (err: any) {
      toast({ title: "Erro na ação", description: err.message || "Não foi possível executar.", type: "error" });
    }
  };

  const filteredNotifications = useMemo(() => {
    return notifications.filter((n) => {
      if (filterType === "unread") return !n.is_read;
      if (filterType === "urgent") return ["URGENT", "CRITICAL", "high"].includes(n.priority);
      if (filterType === "tasks") return n.source === "TASKS" || n.type === "task" || n.type === "TASK_OVERDUE";
      if (filterType === "calendar") return n.source === "CALENDAR" || n.type === "CALENDAR_UPCOMING";
      if (filterType === "emails") return n.source === "EMAILS" || n.type === "EMAIL_IMPORTANT" || n.type === "EMAIL_URGENT";
      if (filterType === "studies") return n.source === "STUDIES" || n.type === "STUDY_REMINDER" || n.type === "study";
      if (filterType === "finances") return n.source === "FINANCES" || n.type === "FINANCE_ALERT" || n.type === "finance";
      if (filterType === "agent") return n.source === "AGENT" || n.type === "AGENT_RECOMMENDATION" || n.type === "ai";
      return true;
    });
  }, [notifications, filterType]);

  const getNotificationIcon = (source?: string, type?: string) => {
    const s = (source || type || "").toUpperCase();
    if (s.includes("TASK")) return <CheckCircle2 className="w-4 h-4 text-emerald-400" />;
    if (s.includes("CALENDAR") || s.includes("EVENT")) return <CalendarDays className="w-4 h-4 text-purple-400" />;
    if (s.includes("EMAIL")) return <Mail className="w-4 h-4 text-orange-400" />;
    if (s.includes("STUDY") || s.includes("POMODORO")) return <BookOpen className="w-4 h-4 text-blue-400" />;
    if (s.includes("FINANCE")) return <Wallet className="w-4 h-4 text-green-400" />;
    if (s.includes("AGENT") || s.includes("AI")) return <Sparkles className="w-4 h-4 text-yellow-400" />;
    if (s.includes("SYNC")) return <RefreshCw className="w-4 h-4 text-cyan-400" />;
    return <Bell className="w-4 h-4 text-accent-400" />;
  };

  const getPriorityBadge = (priority: string) => {
    const p = priority.toUpperCase();
    switch (p) {
      case "CRITICAL":
      case "URGENT":
      case "HIGH":
        return <Badge variant="error">Urgente</Badge>;
      case "IMPORTANT":
        return <Badge variant="warning">Importante</Badge>;
      case "NORMAL":
        return <Badge variant="default">Normal</Badge>;
      case "LOW":
        return <Badge variant="secondary">Informativo</Badge>;
      default:
        return null;
    }
  };

  const handleNavigateFromNotification = (notif: Notification) => {
    const s = (notif.source || notif.type || "").toUpperCase();
    if (s.includes("TASK")) setCurrentPage("tasks");
    else if (s.includes("CALENDAR")) setCurrentPage("calendar");
    else if (s.includes("EMAIL")) setCurrentPage("emails");
    else if (s.includes("STUDY")) setCurrentPage("studies");
    else if (s.includes("FINANCE")) setCurrentPage("finances");
    else if (s.includes("AGENT")) setCurrentPage("ai");
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Central de Notificações Inteligentes</h1>
          <p className="text-sm text-surface-400">
            Avisos preditivos, lembretes de agenda, e-mails prioritários e recomendações do Agent.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleMarkAllAsRead}
            className="gap-2 border-surface-700 hover:text-white"
          >
            <CheckCheck className="w-4 h-4" />
            Marcar todas como lidas
          </Button>
        </div>
      </div>

      {/* Summary Highlights */}
      {summary && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          <div className="glass-card p-3 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-accent-500/10 text-accent-400">
              <Bell className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-surface-400">Não Lidas</span>
              <p className="text-lg font-bold text-white">{summary.unread_count}</p>
            </div>
          </div>

          <div className="glass-card p-3 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-red-500/10 text-red-400">
              <AlertTriangle className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-surface-400">Urgentes</span>
              <p className="text-lg font-bold text-white">{summary.urgent_count}</p>
            </div>
          </div>

          <div className="glass-card p-3 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/10 text-amber-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-surface-400">Importantes</span>
              <p className="text-lg font-bold text-white">{summary.important_count}</p>
            </div>
          </div>

          <div className="glass-card p-3 flex items-center gap-3">
            <div className="p-2 rounded-lg bg-surface-800 text-surface-300">
              <ShieldCheck className="w-4 h-4" />
            </div>
            <div>
              <span className="text-xs text-surface-400">Total Ativas</span>
              <p className="text-lg font-bold text-white">{summary.total_count}</p>
            </div>
          </div>
        </div>
      )}

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2 border-b border-surface-800/50">
        {[
          { key: "all", label: "Todas" },
          { key: "unread", label: "Não Lidas" },
          { key: "urgent", label: "Urgentes" },
          { key: "tasks", label: "Tarefas" },
          { key: "calendar", label: "Agenda" },
          { key: "emails", label: "E-mails" },
          { key: "studies", label: "Estudos" },
          { key: "finances", label: "Finanças" },
          { key: "agent", label: "Agent" },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilterType(f.key as any)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              filterType === f.key
                ? "bg-accent-500/20 text-accent-400 border border-accent-500/30"
                : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/60"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingState message="Carregando notificações inteligentes..." />
      ) : filteredNotifications.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-800/50 mb-4 text-surface-500">
            <Bell className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-surface-200 mb-1">
            Nenhuma notificação encontrada
          </h3>
          <p className="text-xs text-surface-400 max-w-sm">
            Você está em dia com todos os seus prazos, alertas e rotinas!
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredNotifications.map((notif) => (
            <div
              key={notif.id}
              className={`glass-card p-4 flex items-start justify-between gap-4 transition-all duration-200 ${
                notif.is_read ? "opacity-60 bg-surface-950/40" : "border-l-4 border-l-accent-500 bg-surface-900/80"
              }`}
            >
              <div className="flex items-start gap-3.5 flex-1 min-w-0">
                <div className="p-2 rounded-lg bg-surface-800 border border-surface-700/60 shrink-0 mt-0.5">
                  {getNotificationIcon(notif.source, notif.type)}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="text-sm font-bold text-white tracking-tight">{notif.title}</h4>
                    {getPriorityBadge(notif.priority)}
                    {!notif.is_read && (
                      <span className="w-2 h-2 rounded-full bg-accent-500" />
                    )}
                  </div>

                  <p className="text-xs text-surface-300 mt-1 leading-relaxed">
                    {notif.message}
                  </p>

                  <div className="flex items-center gap-4 mt-2.5 text-[11px] text-surface-500 flex-wrap">
                    <span>{formatDate(notif.created_at)}</span>
                    <button
                      onClick={() => handleNavigateFromNotification(notif)}
                      className="text-accent-400 hover:text-accent-300 font-medium flex items-center gap-1 cursor-pointer"
                    >
                      <span>Ver no módulo</span>
                      <ArrowRight className="w-3 h-3" />
                    </button>

                    {notif.action_type && (
                      <button
                        onClick={() => handleExecuteAction(notif)}
                        className="text-emerald-400 hover:text-emerald-300 font-semibold flex items-center gap-1 cursor-pointer"
                      >
                        <span>Executar ação segura</span>
                      </button>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-1 shrink-0">
                {!notif.is_read && (
                  <Button
                    size="sm"
                    variant="ghost"
                    onClick={() => handleMarkAsRead(notif.id)}
                    className="h-8 w-8 p-0 text-surface-400 hover:text-white"
                    title="Marcar como lida"
                  >
                    <CheckCheck className="w-4 h-4" />
                  </Button>
                )}

                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleDismiss(notif.id)}
                  className="h-8 w-8 p-0 text-surface-400 hover:text-red-400"
                  title="Dispensar notificação"
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

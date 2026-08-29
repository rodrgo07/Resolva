import { useState, useEffect, useMemo } from "react";
import { 
  Bell, CheckCheck, CheckCircle2, 
  Wallet, BookOpen, ArrowRight
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
  const { notifications, setNotifications, markAsRead, markAllAsRead } = useNotificationStore();
  const { setCurrentPage } = useAppStore();
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState<"all" | "unread" | "task" | "finance" | "system">("all");
  const { toast } = useToast();

  const loadNotifications = async () => {
    try {
      setIsLoading(true);
      const data = await api.get<Notification[]>("/api/notifications/");
      setNotifications(data || []);
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
      await api.put(`/api/notifications/${id}/read`, {});
      markAsRead(id);
      toast({ title: "Notificação marcada como lida", type: "info" });
    } catch {
      toast({ title: "Erro ao atualizar notificação", type: "error" });
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await api.post("/api/notifications/read-all", {});
      markAllAsRead();
      toast({ title: "Todas as notificações foram marcadas como lidas", type: "success" });
    } catch {
      toast({ title: "Erro ao marcar todas como lidas", type: "error" });
    }
  };

  const filteredNotifications = useMemo(() => {
    return notifications.filter((n) => {
      if (filterType === "unread") return !n.is_read;
      if (filterType === "task") return n.type === "task";
      if (filterType === "finance") return n.type === "finance";
      if (filterType === "system") return n.type === "system";
      return true;
    });
  }, [notifications, filterType]);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case "task":
        return <CheckCircle2 className="w-4 h-4 text-accent-400" />;
      case "finance":
        return <Wallet className="w-4 h-4 text-green-400" />;
      case "study":
        return <BookOpen className="w-4 h-4 text-blue-400" />;
      default:
        return <Bell className="w-4 h-4 text-yellow-400" />;
    }
  };

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case "high":
        return <Badge variant="error">Urgente</Badge>;
      case "normal":
        return <Badge variant="default">Normal</Badge>;
      case "low":
        return <Badge variant="secondary">Informativo</Badge>;
      default:
        return null;
    }
  };

  const handleNavigateFromNotification = (type: string) => {
    if (type === "task") setCurrentPage("tasks");
    else if (type === "finance") setCurrentPage("finances");
    else if (type === "study") setCurrentPage("studies");
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Notificações</h1>
          <p className="text-sm text-surface-400">
            Avisos de tarefas, prazos, alertas financeiros e mensagens de sistema.
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

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {[
          { key: "all", label: "Todas" },
          { key: "unread", label: "Não Lidas" },
          { key: "task", label: "Tarefas" },
          { key: "finance", label: "Finanças" },
          { key: "system", label: "Sistema" },
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
        <LoadingState message="Carregando notificações..." />
      ) : filteredNotifications.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-800/50 mb-4 text-surface-500">
            <Bell className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-surface-200 mb-1">
            Nenhuma notificação encontrada
          </h3>
          <p className="text-xs text-surface-400 max-w-sm">
            Você está em dia com todos os seus alertas e compromissos!
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
                  {getNotificationIcon(notif.type)}
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

                  <div className="flex items-center gap-4 mt-2.5 text-[11px] text-surface-500">
                    <span>{formatDate(notif.created_at)}</span>
                    {["task", "finance", "study"].includes(notif.type) && (
                      <button
                        onClick={() => handleNavigateFromNotification(notif.type)}
                        className="text-accent-400 hover:text-accent-300 font-medium flex items-center gap-1 cursor-pointer"
                      >
                        <span>Abrir módulo</span>
                        <ArrowRight className="w-3 h-3" />
                      </button>
                    )}
                  </div>
                </div>
              </div>

              {!notif.is_read && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleMarkAsRead(notif.id)}
                  className="h-8 px-2 text-xs text-surface-400 hover:text-white shrink-0"
                  title="Marcar como lida"
                >
                  <CheckCheck className="w-4 h-4" />
                </Button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

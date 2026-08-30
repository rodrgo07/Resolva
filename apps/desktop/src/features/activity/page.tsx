import { useState, useEffect, useMemo } from "react";
import { 
  Activity, CheckCircle2, Wallet, BookOpen, Zap
} from "lucide-react";
import { api } from "@/lib/api-client";
import { LoadingState } from "@/components/shared/loading-state";
import { formatDate } from "@/lib/utils";

interface ActivityLog {
  id: number;
  type: string;
  action: string;
  description: string;
  metadata: Record<string, any> | null;
  created_at: string;
}

export function ActivityPage() {
  const [activities, setActivities] = useState<ActivityLog[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filterType, setFilterType] = useState<string>("all");

  const loadActivities = async () => {
    try {
      setIsLoading(true);
      const data = await api.get<ActivityLog[]>("/api/activity/");
      setActivities(data || []);
    } catch {
      setActivities([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadActivities();
  }, []);

  const filteredActivities = useMemo(() => {
    if (filterType === "all") return activities;
    return activities.filter((a) => a.type === filterType);
  }, [activities, filterType]);

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "task": return <CheckCircle2 className="w-4 h-4 text-accent-light" />;
      case "finance": return <Wallet className="w-4 h-4 text-success" />;
      case "study": return <BookOpen className="w-4 h-4 text-info" />;
      case "automation": return <Zap className="w-4 h-4 text-warning" />;
      default: return <Activity className="w-4 h-4 text-text-secondary" />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Linha do Tempo de Atividades</h1>
          <p className="text-sm text-text-secondary">
            Registro cronológico e transparente de tudo o que foi realizado no Resolva.
          </p>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1">
        {[
          { key: "all", label: "Todas as Atividades" },
          { key: "task", label: "Tarefas" },
          { key: "finance", label: "Finanças" },
          { key: "study", label: "Estudos" },
          { key: "automation", label: "Automações" },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilterType(f.key)}
            className={`px-3.5 py-1.5 rounded-lg text-xs font-semibold transition-all cursor-pointer whitespace-nowrap ${
              filterType === f.key
                ? "bg-accent/20 text-accent-light border border-accent/30"
                : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated/60"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingState message="Carregando linha do tempo..." />
      ) : filteredActivities.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-elevated/50 mb-4 text-text-muted">
            <Activity className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-text-primary mb-1">
            Nenhuma atividade recente
          </h3>
          <p className="text-xs text-text-secondary max-w-sm">
            Conclua tarefas, registre sessões de estudo ou acione rotinas para preencher sua linha do tempo.
          </p>
        </div>
      ) : (
        <div className="relative border-l-2 border-border ml-4 pl-6 space-y-6">
          {filteredActivities.map((act) => (
            <div key={act.id} className="relative group">
              {/* Timeline Bullet */}
              <div className="absolute -left-[35px] top-1.5 w-6 h-6 rounded-full bg-surface border-2 border-border group-hover:border-accent flex items-center justify-center transition-colors">
                <div className="w-2 h-2 rounded-full bg-accent-400" />
              </div>

              {/* Card */}
              <div className="glass-card p-4 hover:border-border-strong transition-colors space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {getActivityIcon(act.type)}
                    <span className="text-xs font-bold text-text-primary uppercase tracking-wider">
                      {act.action}
                    </span>
                  </div>
                  <span className="text-[11px] text-text-muted">
                    {formatDate(act.created_at)}
                  </span>
                </div>

                <p className="text-xs text-text-secondary leading-relaxed">
                  {act.description}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

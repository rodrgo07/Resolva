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
      case "task": return <CheckCircle2 className="w-4 h-4 text-accent-400" />;
      case "finance": return <Wallet className="w-4 h-4 text-green-400" />;
      case "study": return <BookOpen className="w-4 h-4 text-blue-400" />;
      case "automation": return <Zap className="w-4 h-4 text-yellow-400" />;
      default: return <Activity className="w-4 h-4 text-surface-400" />;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Linha do Tempo de Atividades</h1>
          <p className="text-sm text-surface-400">
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
        <LoadingState message="Carregando linha do tempo..." />
      ) : filteredActivities.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-800/50 mb-4 text-surface-500">
            <Activity className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-surface-200 mb-1">
            Nenhuma atividade recente
          </h3>
          <p className="text-xs text-surface-400 max-w-sm">
            Conclua tarefas, registre sessões de estudo ou acione rotinas para preencher sua linha do tempo.
          </p>
        </div>
      ) : (
        <div className="relative border-l-2 border-surface-800 ml-4 pl-6 space-y-6">
          {filteredActivities.map((act) => (
            <div key={act.id} className="relative group">
              {/* Timeline Bullet */}
              <div className="absolute -left-[35px] top-1.5 w-6 h-6 rounded-full bg-surface-900 border-2 border-surface-700 group-hover:border-accent-500 flex items-center justify-center transition-colors">
                <div className="w-2 h-2 rounded-full bg-accent-400" />
              </div>

              {/* Card */}
              <div className="glass-card p-4 hover:border-surface-600 transition-colors space-y-1.5">
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2">
                    {getActivityIcon(act.type)}
                    <span className="text-xs font-bold text-white uppercase tracking-wider">
                      {act.action}
                    </span>
                  </div>
                  <span className="text-[11px] text-surface-500">
                    {formatDate(act.created_at)}
                  </span>
                </div>

                <p className="text-xs text-surface-300 leading-relaxed">
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

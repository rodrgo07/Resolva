import { useState, useEffect } from "react";
import { 
  Sparkles, Play, CheckCircle2,
  Clock, AlertTriangle, Layers,
  Compass
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";

interface WorkflowCandidate {
  workflow_id: string;
  name: string;
  score: number;
  confidence: number;
  priority: string;
  required_confirmation: boolean;
  estimated_duration_seconds: number;
  reason: string;
  factors: string[];
  action_preview: string[];
}

interface OrchestrationRun {
  id: number;
  run_id: string;
  status: string;
  trigger_type: string;
  is_dry_run: boolean;
  total_steps: number;
  completed_steps: number;
  error?: string;
  created_at: string;
}

export function OrchestrationDashboard() {
  const { toast } = useToast();
  const [candidates, setCandidates] = useState<WorkflowCandidate[]>([]);
  const [runs, setRuns] = useState<OrchestrationRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [isRunning, setIsRunning] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [cands, rns] = await Promise.all([
        api.get<WorkflowCandidate[]>("/api/orchestration/recommendations"),
        api.get<OrchestrationRun[]>("/api/orchestration/runs?limit=15")
      ]);
      setCandidates(cands || []);
      setRuns(rns || []);
    } catch {
      toast({ title: "Erro", description: "Falha ao carregar dados de orquestração.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleSimulate = async () => {
    try {
      const sim = await api.post<any>("/api/orchestration/simulate", {
        device_id: "DESKTOP-MAIN",
        is_dry_run: true
      });
      toast({
        title: "Simulação de Orquestração Concluída",
        description: "Plano verificado com sucesso (" + sim.total_steps + " etapas previstas sem efeitos colaterais).",
        type: "success"
      });
    } catch {
      toast({ title: "Erro", description: "Falha na simulação.", type: "error" });
    }
  };

  const handleRunOrchestration = async () => {
    setIsRunning(true);
    try {
      await api.post("/api/orchestration/run", {
        trigger_type: "MANUAL",
        device_id: "DESKTOP-MAIN",
        is_dry_run: false
      });
      toast({
        title: "Orquestração Iniciada",
        description: "Execução adaptativa dos workflows prioritários em andamento.",
        type: "success"
      });
      fetchData();
    } catch {
      toast({ title: "Erro", description: "Falha ao iniciar orquestração.", type: "error" });
    } finally {
      setIsRunning(false);
    }
  };

  if (loading) return <LoadingState message="Carregando Inteligência de Orquestração..." />;

  return (
    <div className="space-y-6 animate-fade-in p-2">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Compass className="w-5 h-5 text-accent-400" />
            Orquestração Inteligente & Workflows Adaptativos
          </h2>
          <p className="text-xs text-surface-400 mt-1">
            Planejamento contextual, scoring determinístico, mitigação de conflitos e human-in-the-loop.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handleSimulate}
            className="text-xs border-surface-700 text-surface-300 hover:text-white gap-1.5"
          >
            <Layers className="w-4 h-4 text-accent-400" /> Simular Plano (Dry Run)
          </Button>

          <Button
            size="sm"
            onClick={handleRunOrchestration}
            disabled={isRunning}
            className="gap-1.5 bg-accent-600 hover:bg-accent-700 text-xs text-white"
          >
            <Play className="w-4 h-4" /> Executar Orquestração
          </Button>
        </div>
      </div>

      {/* Grid de Recomendações e Scoring */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-surface-400 uppercase tracking-wider flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-accent-400" />
          Workflows Selecionados por Relevância Contextual ({candidates.length})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {candidates.map((cand) => (
            <div key={cand.workflow_id} className="glass-card p-4 rounded-xl border border-surface-800 bg-surface-950/60 flex flex-col justify-between space-y-3">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <Badge variant={cand.score >= 80 ? "warning" : "secondary"} className="text-[10px]">
                    Score: {cand.score} pts
                  </Badge>
                  <span className="text-[10px] text-surface-400 font-mono flex items-center gap-1">
                    <Clock className="w-3 h-3" /> ~{cand.estimated_duration_seconds}s
                  </span>
                </div>

                <h4 className="text-sm font-bold text-white">{cand.name}</h4>
                <p className="text-xs text-surface-400">{cand.reason}</p>

                <div className="p-2 rounded-lg bg-surface-900/70 border border-surface-800/80 space-y-1">
                  <span className="text-[9px] font-bold text-surface-400 uppercase">Fatores Analisados:</span>
                  {cand.factors.map((f, idx) => (
                    <div key={idx} className="text-[11px] text-surface-300 flex items-start gap-1.5">
                      <span className="text-accent-400">•</span>
                      <span>{f}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="pt-2 border-t border-surface-800/60 flex items-center justify-between text-[10px] text-surface-400">
                <span>{cand.action_preview.length} ações</span>
                {cand.required_confirmation ? (
                  <span className="text-yellow-400 flex items-center gap-1 font-medium">
                    <AlertTriangle className="w-3 h-3" /> Exige Confirmação
                  </span>
                ) : (
                  <span className="text-green-400 flex items-center gap-1 font-medium">
                    <CheckCircle2 className="w-3 h-3" /> Auto Seguro
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Histórico Recente de Orquestrações */}
      <div className="space-y-3 pt-4 border-t border-surface-800">
        <h3 className="text-xs font-bold text-surface-400 uppercase tracking-wider">
          Histórico de Execuções e Auditoria ({runs.length})
        </h3>

        <div className="space-y-2">
          {runs.map((r) => (
            <div key={r.run_id} className="p-3 rounded-xl border border-surface-800 bg-surface-900/50 flex items-center justify-between text-xs">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-accent-400 font-bold">#{r.run_id.slice(-8)}</span>
                  <Badge variant={r.status === "COMPLETED" ? "success" : r.status === "FAILED" ? "error" : "warning"} className="text-[10px]">
                    {r.status}
                  </Badge>
                  {r.is_dry_run && <Badge variant="outline" className="text-[9px]">DRY RUN</Badge>}
                </div>
                <p className="text-[11px] text-surface-400">
                  Progresso: {r.completed_steps} de {r.total_steps} etapas concluídas • Disparo: {r.trigger_type}
                </p>
              </div>
              <span className="text-[10px] text-surface-400 font-mono">
                {new Date(r.created_at).toLocaleTimeString()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

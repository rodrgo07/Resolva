import { useState, useEffect } from "react";
import { 
  Activity, Shield, CheckCircle2,
  Database, RefreshCw, Smartphone, HardDrive,
  Cpu, Radio
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";

export function SystemHealthDashboard() {
  const { toast } = useToast();
  const [health, setHealth] = useState<any>(null);
  const [safety, setSafety] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [h, s] = await Promise.all([
        api.get<any>("/api/system/health"),
        api.get<any>("/api/system/safety")
      ]);
      setHealth(h);
      setSafety(s);
    } catch {
      toast({ title: "Erro", description: "Falha ao consultar saúde do sistema.", type: "error" });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleToggleSafeMode = async () => {
    if (!safety) return;
    const newSafeMode = !safety.global_safe_mode;
    try {
      await api.post("/api/system/safety", {
        global_safe_mode: newSafeMode
      });
      toast({
        title: newSafeMode ? "Modo Seguro Ativado" : "Modo Seguro Desativado",
        description: newSafeMode 
          ? "Operações de modificação bloqueadas para segurança." 
          : "Operação normal restabelecida.",
        type: "success"
      });
      fetchData();
    } catch {
      toast({ title: "Erro", description: "Falha ao alterar Modo Seguro.", type: "error" });
    }
  };

  if (loading) return <LoadingState message="Diagnosticando Subsistemas do RESOLVA..." />;

  return (
    <div className="space-y-6 animate-fade-in p-2">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h2 className="text-lg font-bold text-text-primary flex items-center gap-2">
            <Activity className="w-5 h-5 text-accent-light" />
            Central de Saúde, Diagnóstico & Hardening (Release 1.0)
          </h2>
          <p className="text-xs text-text-secondary mt-1">
            Monitoramento de latência, integridade do SQLite, isolamento de segurança e políticas de autonomia.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={fetchData}
            className="text-xs border-border text-text-secondary hover:text-text-primary gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Atualizar Diagnóstico
          </Button>

          <Button
            size="sm"
            onClick={handleToggleSafeMode}
            className={"gap-1.5 text-xs text-text-primary " + (safety?.global_safe_mode ? "bg-red-600 hover:bg-red-700" : "bg-accent hover:bg-accent")}
          >
            <Shield className="w-4 h-4" />
            {safety?.global_safe_mode ? "Desativar SAFE_MODE" : "Ativar SAFE_MODE"}
          </Button>
        </div>
      </div>

      {/* Banner de Estado Geral */}
      <div className={"p-4 rounded-xl border flex items-center justify-between " + (safety?.global_safe_mode ? "bg-red-950/40 border-red-800/80" : "bg-background/60 border-border")}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-text-primary">
              Status Geral do Sistema:
            </span>
            <Badge variant={health?.overall_status === "HEALTHY" ? "success" : "warning"} className="text-[10px]">
              {health?.overall_status}
            </Badge>
            {safety?.global_safe_mode && (
              <Badge variant="error" className="text-[10px]">
                SAFE_MODE ATIVO
              </Badge>
            )}
          </div>
          <p className="text-xs text-text-secondary">
            Tempo de atividade: {health?.metrics_summary?.uptime_seconds}s • Memória estimada: {health?.metrics_summary?.memory_mb} MB
          </p>
        </div>
      </div>

      {/* Grid de Subsistemas */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-text-secondary uppercase tracking-wider">
          Subsistemas Monitorados ({health?.components ? Object.keys(health.components).length : 0})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {health?.components && Object.entries(health.components).map(([key, comp]: [string, any]) => (
            <div key={key} className="glass-card p-4 rounded-xl border border-border bg-background/60 flex flex-col justify-between space-y-3">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-text-primary flex items-center gap-1.5">
                    {key === "database" && <Database className="w-3.5 h-3.5 text-accent-light" />}
                    {key === "devices" && <Smartphone className="w-3.5 h-3.5 text-accent-light" />}
                    {key === "backup" && <HardDrive className="w-3.5 h-3.5 text-accent-light" />}
                    {key === "sync_engine" && <RefreshCw className="w-3.5 h-3.5 text-accent-light" />}
                    {key === "orchestration" && <Cpu className="w-3.5 h-3.5 text-accent-light" />}
                    {key === "event_bus" && <Radio className="w-3.5 h-3.5 text-accent-light" />}
                    {comp.component}
                  </span>
                  <Badge variant={comp.status === "HEALTHY" ? "success" : "warning"} className="text-[9px]">
                    {comp.status}
                  </Badge>
                </div>
                <p className="text-xs text-text-secondary">{comp.message}</p>
              </div>

              <div className="pt-2 border-t border-border/60 flex items-center justify-between text-[10px] text-text-secondary">
                <span>Latência: {comp.latency_ms}ms</span>
                <span className="text-success flex items-center gap-1">
                  <CheckCircle2 className="w-3 h-3" /> Monitorado
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

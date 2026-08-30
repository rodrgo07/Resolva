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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800 pb-4">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Activity className="w-5 h-5 text-accent-400" />
            Central de Saúde, Diagnóstico & Hardening (Release 1.0)
          </h2>
          <p className="text-xs text-surface-400 mt-1">
            Monitoramento de latência, integridade do SQLite, isolamento de segurança e políticas de autonomia.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={fetchData}
            className="text-xs border-surface-700 text-surface-300 hover:text-white gap-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" /> Atualizar Diagnóstico
          </Button>

          <Button
            size="sm"
            onClick={handleToggleSafeMode}
            className={"gap-1.5 text-xs text-white " + (safety?.global_safe_mode ? "bg-red-600 hover:bg-red-700" : "bg-accent-600 hover:bg-accent-700")}
          >
            <Shield className="w-4 h-4" />
            {safety?.global_safe_mode ? "Desativar SAFE_MODE" : "Ativar SAFE_MODE"}
          </Button>
        </div>
      </div>

      {/* Banner de Estado Geral */}
      <div className={"p-4 rounded-xl border flex items-center justify-between " + (safety?.global_safe_mode ? "bg-red-950/40 border-red-800/80" : "bg-surface-950/60 border-surface-800")}>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <span className="text-sm font-bold text-white">
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
          <p className="text-xs text-surface-400">
            Tempo de atividade: {health?.metrics_summary?.uptime_seconds}s • Memória estimada: {health?.metrics_summary?.memory_mb} MB
          </p>
        </div>
      </div>

      {/* Grid de Subsistemas */}
      <div className="space-y-3">
        <h3 className="text-xs font-bold text-surface-400 uppercase tracking-wider">
          Subsistemas Monitorados ({health?.components ? Object.keys(health.components).length : 0})
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {health?.components && Object.entries(health.components).map(([key, comp]: [string, any]) => (
            <div key={key} className="glass-card p-4 rounded-xl border border-surface-800 bg-surface-950/60 flex flex-col justify-between space-y-3">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold text-white flex items-center gap-1.5">
                    {key === "database" && <Database className="w-3.5 h-3.5 text-accent-400" />}
                    {key === "devices" && <Smartphone className="w-3.5 h-3.5 text-accent-400" />}
                    {key === "backup" && <HardDrive className="w-3.5 h-3.5 text-accent-400" />}
                    {key === "sync_engine" && <RefreshCw className="w-3.5 h-3.5 text-accent-400" />}
                    {key === "orchestration" && <Cpu className="w-3.5 h-3.5 text-accent-400" />}
                    {key === "event_bus" && <Radio className="w-3.5 h-3.5 text-accent-400" />}
                    {comp.component}
                  </span>
                  <Badge variant={comp.status === "HEALTHY" ? "success" : "warning"} className="text-[9px]">
                    {comp.status}
                  </Badge>
                </div>
                <p className="text-xs text-surface-300">{comp.message}</p>
              </div>

              <div className="pt-2 border-t border-surface-800/60 flex items-center justify-between text-[10px] text-surface-400">
                <span>Latência: {comp.latency_ms}ms</span>
                <span className="text-green-400 flex items-center gap-1">
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

import { useState, useEffect } from "react";
import { 
  Sparkles, Clock, Play, Pause, Square, ExternalLink,
  Smartphone
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { api } from "@/lib/api-client";
import { useAppStore } from "@/stores/app-store";

interface LiveState {
  session_id: string;
  type: string;
  status: string;
  duration_seconds: number;
  remaining_seconds: number;
  current_block_id?: string;
  origin_device_id: string;
}

export function SmartWidget() {
  const { setCurrentPage } = useAppStore();
  const [timeRemaining, setTimeRemaining] = useState(1500);
  const [isRunning, setIsRunning] = useState(false);
  const [recommendation] = useState<string>("Finalizar tarefas prioritárias antes da próxima reunião.");


  const fetchLiveState = async () => {
    try {
      const res = await api.get<{ active_session: LiveState }>("/api/realtime/state");
      if (res.active_session) {
        setTimeRemaining(res.active_session.remaining_seconds);
        setIsRunning(res.active_session.status === "RUNNING");
      }
    } catch {}
  };

  useEffect(() => {
    fetchLiveState();
    const interval = setInterval(fetchLiveState, 5000);
    return () => clearInterval(interval);
  }, []);

  // Timer local fluido
  useEffect(() => {
    let t: any = null;
    if (isRunning && timeRemaining > 0) {
      t = setInterval(() => {
        setTimeRemaining((s) => {
          if (s <= 1) {
            setIsRunning(false);
            return 0;
          }
          return s - 1;
        });
      }, 1000);
    }
    return () => clearInterval(t);
  }, [isRunning, timeRemaining]);

  const handleAction = async (action: "START" | "PAUSE" | "RESUME" | "COMPLETE") => {
    try {
      const res = await api.post<LiveState>("/api/realtime/state/action", {
        device_id: "DESKTOP-WIDGET",
        type: "POMODORO",
        action: action,
        duration_seconds: 1500
      });
      setTimeRemaining(res.remaining_seconds);
      setIsRunning(res.status === "RUNNING");
    } catch {}
  };


  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
  };

  return (
    <div className="w-80 glass-card p-4 bg-background/90 border border-border/80 shadow-2xl rounded-2xl text-text-primary select-none animate-fade-in space-y-3.5">
      {/* Header Compacto */}
      <div className="flex items-center justify-between border-b border-border/80 pb-2.5">
        <div className="flex items-center gap-2">
          <div className="w-5 h-5 rounded-md bg-accent flex items-center justify-center font-bold text-[10px] text-text-primary">
            R
          </div>
          <span className="font-bold text-xs tracking-wider text-text-primary">RESOLVA LIVE</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] text-text-secondary font-mono">Sync Ativo</span>
        </div>
      </div>

      {/* Card AGORA / Foco Atual */}
      <div className="p-3 rounded-xl bg-surface/80 border border-border space-y-2">
        <div className="flex items-center justify-between text-[10px]">
          <span className="text-accent-light font-bold uppercase tracking-wider flex items-center gap-1">
            <Clock className="w-3 h-3" /> Foco Profundo
          </span>
          <span className="font-mono text-text-primary text-xs font-bold">{formatTime(timeRemaining)}</span>
        </div>

        {/* Controles Rápidos */}
        <div className="flex items-center gap-2 pt-1">
          <Button
            size="sm"
            onClick={() => handleAction(isRunning ? "PAUSE" : (timeRemaining < 1500 && timeRemaining > 0 ? "RESUME" : "START"))}
            className={`h-7 flex-1 text-xs font-bold gap-1 rounded-lg ${isRunning ? "bg-amber-600 hover:bg-amber-700" : "bg-accent hover:bg-accent"}`}
          >
            {isRunning ? <Pause className="w-3 h-3" /> : <Play className="w-3 h-3" />}
            {isRunning ? "Pausar" : "Iniciar"}
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => handleAction("COMPLETE")}
            className="h-7 px-2 border-border hover:bg-surface-elevated text-text-secondary hover:text-text-primary rounded-lg"
            title="Finalizar Bloco"
          >
            <Square className="w-3 h-3" />
          </Button>
        </div>
      </div>


      {/* Proactive Recommendation */}
      <div className="p-2.5 rounded-xl bg-accent/10 border border-accent/20 text-xs space-y-1">
        <div className="flex items-center gap-1 text-[10px] font-bold text-accent-light">
          <Sparkles className="w-3 h-3" /> Sugestão do Agent
        </div>
        <p className="text-[11px] text-text-secondary leading-snug">{recommendation}</p>
      </div>

      {/* Footer / Abrir Completo */}
      <div className="pt-1 flex items-center justify-between text-[10px] text-text-secondary">
        <button 
          onClick={() => setCurrentPage("dashboard")}
          className="flex items-center gap-1 hover:text-text-primary transition-colors cursor-pointer"
        >
          <ExternalLink className="w-3 h-3" /> Abrir Resolva
        </button>
        <span className="flex items-center gap-1">
          <Smartphone className="w-3 h-3 text-text-secondary" />
          <span>Mobile Pareado</span>
        </span>
      </div>
    </div>
  );
}

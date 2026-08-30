import { useState, useEffect } from "react";
import { 
  Plus, BookOpen, Timer, Play, Pause, RotateCcw, 
  CheckCircle2, Clock, Trash2, Edit3, Award, Calendar, Layers
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { ConfirmationDialog } from "@/components/shared/confirmation-dialog";
import { LoadingState } from "@/components/shared/loading-state";
import { formatDate } from "@/lib/utils";

interface StudySubject {
  id: number;
  name: string;
  description: string | null;
  priority: number;
  progress: number;
  weekly_goal_hours: number | null;
  monthly_goal_hours: number | null;
  color: string | null;
  created_at: string;
}

interface StudySession {
  id: number;
  subject_id: number;
  mode: "pomodoro" | "free";
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
  notes: string | null;
}

interface StudySummary {
  hours_today: number;
  hours_this_week: number;
  hours_this_month: number;
}

export function StudiesPage() {
  const [subjects, setSubjects] = useState<StudySubject[]>([]);
  const [sessions, setSessions] = useState<StudySession[]>([]);
  const [summary, setSummary] = useState<StudySummary>({ hours_today: 0, hours_this_week: 0, hours_this_month: 0 });
  const [isLoading, setIsLoading] = useState(true);

  // Tabs
  const [activeTab, setActiveTab] = useState<"subjects" | "timer" | "sessions">("subjects");

  // Subject Modal states
  const [isSubjectModalOpen, setIsSubjectModalOpen] = useState(false);
  const [editingSubject, setEditingSubject] = useState<StudySubject | null>(null);
  const [deleteSubjectId, setDeleteSubjectId] = useState<number | null>(null);

  // Subject Form inputs
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(1);
  const [weeklyGoal, setWeeklyGoal] = useState("5");
  const [monthlyGoal, setMonthlyGoal] = useState("20");
  const [color, setColor] = useState("#8b5cf6");
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Timer State (Pomodoro / Free)
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | "">("");
  const [timerMode, setTimerMode] = useState<"pomodoro" | "short_break" | "free">("pomodoro");
  const [timeLeft, setTimeLeft] = useState(25 * 60);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [sessionNotes, setSessionNotes] = useState("");

  const { toast } = useToast();

  const loadStudiesData = async () => {
    try {
      setIsLoading(true);
      const [subsData, sessData, sumData] = await Promise.allSettled([
        api.get<StudySubject[]>("/api/studies/subjects"),
        api.get<StudySession[]>("/api/studies/sessions"),
        api.get<StudySummary>("/api/studies/summary"),
      ]);

      if (subsData.status === "fulfilled") {
        const subs = subsData.value || [];
        setSubjects(subs);
        if (subs.length > 0 && selectedSubjectId === "") {
          setSelectedSubjectId(subs[0].id);
        }
      }
      if (sessData.status === "fulfilled") setSessions(sessData.value || []);
      if (sumData.status === "fulfilled") setSummary(sumData.value);
    } catch {
      toast({ title: "Erro ao carregar dados de estudos", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadStudiesData();
  }, []);

  // Timer countdown hook
  useEffect(() => {
    let interval: NodeJS.Timeout | null = null;

    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (timerMode === "free") {
            return prev + 1; // count up for free mode
          } else {
            if (prev <= 1) {
              setIsTimerRunning(false);
              handleTimerComplete();
              return 0;
            }
            return prev - 1;
          }
        });
      }, 1000);
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [isTimerRunning, timerMode]);

  const handleTimerComplete = async () => {
    toast({ title: "Sessão finalizada! Bom trabalho!", type: "success" });
    if (timerMode === "pomodoro" && selectedSubjectId) {
      await saveSession(25);
    }
  };

  const handleModeChange = (mode: "pomodoro" | "short_break" | "free") => {
    setIsTimerRunning(false);
    setTimerMode(mode);
    if (mode === "pomodoro") setTimeLeft(25 * 60);
    else if (mode === "short_break") setTimeLeft(5 * 60);
    else if (mode === "free") setTimeLeft(0);
  };

  const saveSession = async (durationMins: number) => {
    if (!selectedSubjectId) return;
    try {
      await api.post("/api/studies/sessions", {
        subject_id: Number(selectedSubjectId),
        mode: timerMode === "free" ? "free" : "pomodoro",
        started_at: new Date().toISOString(),
        ended_at: new Date().toISOString(),
        duration_minutes: durationMins,
        notes: sessionNotes.trim() || null,
      });
      setSessionNotes("");
      loadStudiesData();
    } catch {
      toast({ title: "Erro ao registrar sessão", type: "error" });
    }
  };

  const handleManualFinish = async () => {
    setIsTimerRunning(false);
    const durationMins = Math.max(1, Math.round(timeLeft / 60));
    if (selectedSubjectId && durationMins > 0) {
      await saveSession(durationMins);
      toast({ title: `Sessão de ${durationMins} minutos registrada!`, type: "success" });
    }
    setTimeLeft(0);
  };

  const formatTimer = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`;
  };

  const handleOpenCreateSubject = () => {
    setEditingSubject(null);
    setName("");
    setDescription("");
    setPriority(1);
    setWeeklyGoal("5");
    setMonthlyGoal("20");
    setColor("#8b5cf6");
    setIsSubjectModalOpen(true);
  };

  const handleOpenEditSubject = (subj: StudySubject) => {
    setEditingSubject(subj);
    setName(subj.name);
    setDescription(subj.description || "");
    setPriority(subj.priority);
    setWeeklyGoal(String(subj.weekly_goal_hours || 5));
    setMonthlyGoal(String(subj.monthly_goal_hours || 20));
    setColor(subj.color || "#8b5cf6");
    setIsSubjectModalOpen(true);
  };

  const handleSaveSubject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    const payload = {
      name: name.trim(),
      description: description.trim() || null,
      priority: Number(priority),
      weekly_goal_hours: parseFloat(weeklyGoal) || 5.0,
      monthly_goal_hours: parseFloat(monthlyGoal) || 20.0,
      color: color || "#8b5cf6",
    };

    try {
      if (editingSubject) {
        await api.put(`/api/studies/subjects/${editingSubject.id}`, payload);
        toast({ title: "Matéria atualizada com sucesso", type: "success" });
      } else {
        await api.post("/api/studies/subjects", payload);
        toast({ title: "Matéria cadastrada com sucesso", type: "success" });
      }
      setIsSubjectModalOpen(false);
      loadStudiesData();
    } catch {
      toast({ title: "Erro ao salvar matéria", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteSubject = async () => {
    if (!deleteSubjectId) return;
    try {
      await api.delete(`/api/studies/subjects/${deleteSubjectId}`);
      toast({ title: "Matéria excluída", type: "info" });
      setDeleteSubjectId(null);
      loadStudiesData();
    } catch {
      toast({ title: "Erro ao excluir matéria", type: "error" });
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Estudos</h1>
          <p className="text-sm text-text-secondary">
            Acompanhe disciplinas, registre sessões com Pomodoro e atinja suas metas de foco.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button 
            variant="secondary" 
            onClick={() => setActiveTab("timer")} 
            className="gap-2 border border-border"
          >
            <Timer className="w-4 h-4 text-accent-light" />
            Cronômetro
          </Button>
          <Button onClick={handleOpenCreateSubject} className="gap-2">
            <Plus className="w-4 h-4" />
            Nova Matéria
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="glass-card p-5 border-l-4 border-l-blue-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Estudado Hoje</span>
            <Clock className="w-4 h-4 text-info" />
          </div>
          <p className="text-2xl font-bold text-info tracking-tight">
            {summary.hours_today.toFixed(1)}h
          </p>
        </div>

        <div className="glass-card p-5 border-l-4 border-l-accent-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Esta Semana</span>
            <Award className="w-4 h-4 text-accent-light" />
          </div>
          <p className="text-2xl font-bold text-accent-light tracking-tight">
            {summary.hours_this_week.toFixed(1)}h
          </p>
        </div>

        <div className="glass-card p-5 border-l-4 border-l-purple-500">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Este Mês</span>
            <Calendar className="w-4 h-4 text-accent-light" />
          </div>
          <p className="text-2xl font-bold text-accent-light tracking-tight">
            {summary.hours_this_month.toFixed(1)}h
          </p>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-border/60 pb-3">
        {[
          { key: "subjects", label: "Matérias & Metas", icon: BookOpen },
          { key: "timer", label: "Cronômetro & Foco", icon: Timer },
          { key: "sessions", label: "Histórico de Sessões", icon: Layers },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                activeTab === tab.key
                  ? "bg-accent/20 text-accent-light border border-accent/30"
                  : "text-text-secondary hover:text-text-primary hover:bg-surface-elevated/60"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content Area */}
      {isLoading ? (
        <LoadingState message="Carregando matérias e sessões..." />
      ) : activeTab === "subjects" ? (
        /* Subjects Grid */
        <div>
          {subjects.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
              <div className="p-4 rounded-full bg-surface-elevated/50 mb-4 text-text-muted">
                <BookOpen className="w-10 h-10" />
              </div>
              <h3 className="text-base font-semibold text-text-primary mb-1">
                Nenhuma matéria cadastrada
              </h3>
              <p className="text-xs text-text-secondary max-w-sm mb-5">
                Cadastre suas disciplinas para registrar sessões de estudo.
              </p>
              <Button onClick={handleOpenCreateSubject} size="sm" className="gap-1.5">
                <Plus className="w-4 h-4" />
                Cadastrar Matéria
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {subjects.map((subj) => (
                <div 
                  key={subj.id}
                  className="glass-card p-5 flex flex-col justify-between hover:border-border-strong transition-all space-y-4"
                >
                  <div>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex items-center gap-2.5">
                        <div 
                          className="w-3 h-3 rounded-full shrink-0" 
                          style={{ backgroundColor: subj.color || "#8b5cf6" }} 
                        />
                        <h3 className="text-base font-semibold text-text-primary tracking-tight">{subj.name}</h3>
                      </div>
                      <div className="flex items-center gap-1">
                        <button
                          onClick={() => handleOpenEditSubject(subj)}
                          className="p-1 text-text-secondary hover:text-text-primary rounded transition-colors cursor-pointer"
                        >
                          <Edit3 className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => setDeleteSubjectId(subj.id)}
                          className="p-1 text-text-secondary hover:text-error rounded transition-colors cursor-pointer"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </div>

                    {subj.description && (
                      <p className="text-xs text-text-secondary mt-2 line-clamp-2 leading-relaxed">
                        {subj.description}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2 pt-2 border-t border-border/60">
                    <div className="flex items-center justify-between text-xs text-text-secondary">
                      <span>Progresso Geral</span>
                      <span className="font-semibold text-text-primary">{subj.progress}%</span>
                    </div>
                    <div className="w-full bg-surface-elevated rounded-full h-1.5 overflow-hidden">
                      <div 
                        className="bg-accent h-full rounded-full transition-all duration-300"
                        style={{ width: `${subj.progress}%` }}
                      />
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-text-secondary pt-1">
                      <span>Meta Semanal: <strong className="text-text-primary">{subj.weekly_goal_hours || 0}h</strong></span>
                      <Button
                        size="sm"
                        variant="ghost"
                        className="h-7 px-2 text-xs text-accent-light hover:text-accent-300"
                        onClick={() => {
                          setSelectedSubjectId(subj.id);
                          setActiveTab("timer");
                        }}
                      >
                        Estudar →
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      ) : activeTab === "timer" ? (
        /* Pomodoro & Free Timer Tab */
        <div className="max-w-xl mx-auto glass-card p-8 text-center space-y-6">
          {/* Mode Selector */}
          <div className="inline-flex rounded-lg bg-surface-elevated/60 p-1 border border-border/60">
            <button
              onClick={() => handleModeChange("pomodoro")}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-colors cursor-pointer ${
                timerMode === "pomodoro" ? "bg-accent text-text-primary shadow-sm" : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Pomodoro (25m)
            </button>
            <button
              onClick={() => handleModeChange("short_break")}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-colors cursor-pointer ${
                timerMode === "short_break" ? "bg-accent text-text-primary shadow-sm" : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Pausa Curta (5m)
            </button>
            <button
              onClick={() => handleModeChange("free")}
              className={`px-4 py-1.5 rounded-md text-xs font-semibold transition-colors cursor-pointer ${
                timerMode === "free" ? "bg-accent text-text-primary shadow-sm" : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Livre / Contínuo
            </button>
          </div>

          {/* Subject Dropdown */}
          <div className="text-left">
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Matéria em foco</label>
            <select
              value={selectedSubjectId}
              onChange={(e) => setSelectedSubjectId(e.target.value ? Number(e.target.value) : "")}
              className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
            >
              {subjects.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.name}
                </option>
              ))}
            </select>
          </div>

          {/* Timer Display */}
          <div className="py-6">
            <div className="text-7xl font-mono font-bold text-text-primary tracking-widest selection:bg-transparent">
              {formatTimer(timeLeft)}
            </div>
            <p className="text-xs text-text-secondary mt-2">
              {isTimerRunning ? "Sessão em andamento... Mantenha o foco!" : "Pronto para iniciar"}
            </p>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-center gap-4">
            <Button
              size="lg"
              className="px-8 gap-2 font-semibold shadow-lg shadow-accent-600/30"
              onClick={() => setIsTimerRunning(!isTimerRunning)}
            >
              {isTimerRunning ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
              <span>{isTimerRunning ? "Pausar" : "Iniciar Foco"}</span>
            </Button>
            <Button
              variant="outline"
              size="lg"
              onClick={() => {
                setIsTimerRunning(false);
                handleModeChange(timerMode);
              }}
              title="Reiniciar"
            >
              <RotateCcw className="w-5 h-5" />
            </Button>
            {timerMode === "free" && isTimerRunning && (
              <Button
                variant="secondary"
                size="lg"
                onClick={handleManualFinish}
                className="gap-2 text-success border border-green-500/30"
              >
                <CheckCircle2 className="w-5 h-5" />
                <span>Salvar Sessão</span>
              </Button>
            )}
          </div>

          {/* Notes Input */}
          <div className="text-left pt-4 border-t border-border">
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Notas da sessão (opcional)</label>
            <Input
              value={sessionNotes}
              onChange={(e) => setSessionNotes(e.target.value)}
              placeholder="Ex: Resolução de exercícios de álgebra, revisão cap. 3..."
            />
          </div>
        </div>
      ) : (
        /* Sessions History Tab */
        <div className="space-y-3">
          {sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center glass-card border-dashed">
              <p className="text-sm font-semibold text-text-primary">Nenhuma sessão registrada</p>
              <p className="text-xs text-text-secondary mt-1 mb-4">Utilize o cronômetro para marcar seus blocos de foco.</p>
              <Button onClick={() => setActiveTab("timer")} size="sm">Ir para o Cronômetro</Button>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((sess) => {
                const subj = subjects.find(s => s.id === sess.subject_id);
                return (
                  <div
                    key={sess.id}
                    className="glass-card p-4 flex items-center justify-between gap-4 hover:border-border-strong transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="p-2 rounded-lg bg-blue-500/10 text-info">
                        <Clock className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-text-primary">
                            {subj?.name || "Matéria Geral"}
                          </span>
                          <Badge variant="outline" className="text-[10px] py-0 px-1.5 capitalize border-border">
                            {sess.mode}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-text-secondary mt-0.5">
                          <span>{formatDate(sess.started_at)}</span>
                          {sess.notes && <span className="text-text-muted">Obs: {sess.notes}</span>}
                        </div>
                      </div>
                    </div>

                    <span className="text-sm font-bold text-accent-light">
                      {sess.duration_minutes} min
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Create / Edit Subject Modal */}
      <Modal
        isOpen={isSubjectModalOpen}
        onClose={() => setIsSubjectModalOpen(false)}
        title={editingSubject ? "Editar Matéria" : "Nova Matéria de Estudo"}
        size="md"
      >
        <form onSubmit={handleSaveSubject} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Nome da Disciplina *</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Inteligência Artificial, Rust & WebAssembly"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Descrição</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="Objetivos, links para apostilas, tópicos..."
              className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-accent-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Meta Semanal (Horas)</label>
              <Input
                type="number"
                step="0.5"
                value={weeklyGoal}
                onChange={(e) => setWeeklyGoal(e.target.value)}
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Meta Mensal (Horas)</label>
              <Input
                type="number"
                step="1"
                value={monthlyGoal}
                onChange={(e) => setMonthlyGoal(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Prioridade</label>
              <select
                value={priority}
                onChange={(e) => setPriority(Number(e.target.value))}
                className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value={1}>1 - Normal</option>
                <option value={2}>2 - Média</option>
                <option value={3}>3 - Alta</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Cor de Destaque</label>
              <Input
                type="color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                className="h-10 p-1 cursor-pointer"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-border">
            <Button variant="ghost" type="button" onClick={() => setIsSubjectModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Salvar Matéria
            </Button>
          </div>
        </form>
      </Modal>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteSubjectId !== null}
        onClose={() => setDeleteSubjectId(null)}
        onConfirm={handleDeleteSubject}
        title="Excluir Matéria"
        message="Tem certeza que deseja excluir esta matéria de estudos? As sessões associadas permanecerão no histórico."
        confirmLabel="Excluir"
        variant="destructive"
      />
    </div>
  );
}

import { useState, useEffect } from "react";
import { 
  Zap, Play, Plus, Trash2, CheckCircle2, XCircle, 
  Clock, ShieldCheck, Terminal, Layers, RefreshCw, FileText,
  Power, Sparkles, Check
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

interface AutomationTrigger {
  id?: number;
  type: string;
  config: Record<string, any>;
}

interface AutomationAction {
  id?: number;
  type: string;
  config: Record<string, any>;
  sort_order: number;
  requires_confirmation: boolean;
}

interface Automation {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  icon: string | null;
  triggers: AutomationTrigger[];
  actions: AutomationAction[];
  created_at: string;
}

interface AutomationExecution {
  id: number;
  automation_id: number;
  status: "completed" | "running" | "failed";
  started_at: string;
  ended_at: string | null;
  log: string | null;
  error_message: string | null;
}

interface Template {
  id: string;
  name: string;
  description: string;
  trigger: AutomationTrigger;
  actions: AutomationAction[];
  risk_level: string;
  requires_confirmation: boolean;
}

export function AutomationsPage() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [templates, setTemplates] = useState<Template[]>([]);
  const [executions, setExecutions] = useState<AutomationExecution[]>([]);
  const [selectedAutoId, setSelectedAutoId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [runningId, setRunningId] = useState<number | null>(null);
  const [isKillSwitchActive, setIsKillSwitchActive] = useState(false);

  // Tabs
  const [activeTab, setActiveTab] = useState<"automations" | "templates" | "executions">("automations");

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // Form states (Wizard)
  const [] = useState<1 | 2 | 3>(1);
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [triggerType, setTriggerType] = useState<"SCHEDULE" | "MANUAL" | "APP_START">("SCHEDULE");
  const [scheduleTime, setScheduleTime] = useState("08:00");
  const [actionType, setActionType] = useState<"CREATE_NOTIFICATION" | "OPEN_APPLICATION" | "START_STUDY_SESSION" | "SHOW_AGENT_MESSAGE">("CREATE_NOTIFICATION");
  const [appName, setAppName] = useState("vscode");
  const [notifTitle, setNotifTitle] = useState("Rotina Executada");
  const [notifMsg, setNotifMsg] = useState("Sua automação foi concluída com sucesso.");
  const [studyDuration, setStudyDuration] = useState(25);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { toast } = useToast();

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [autos, tpls, ksRes] = await Promise.allSettled([
        api.get<Automation[]>("/api/automations/"),
        api.get<Template[]>("/api/automations/templates"),
        api.get<{ is_active: boolean }>("/api/automations/kill-switch/status"),
      ]);

      if (autos.status === "fulfilled") {
        setAutomations(autos.value || []);
        if (autos.value && autos.value.length > 0 && selectedAutoId === null) {
          setSelectedAutoId(autos.value[0].id);
          loadExecutions(autos.value[0].id);
        }
      }
      if (tpls.status === "fulfilled") {
        setTemplates(tpls.value || []);
      }
      if (ksRes.status === "fulfilled") {
        setIsKillSwitchActive(ksRes.value?.is_active || false);
      }
    } catch {
      toast({ title: "Erro ao carregar automações", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  const loadExecutions = async (autoId: number) => {
    try {
      const execs = await api.get<AutomationExecution[]>(`/api/automations/${autoId}/executions`);
      setExecutions(execs || []);
    } catch {
      setExecutions([]);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSelectAutomation = (id: number) => {
    setSelectedAutoId(id);
    loadExecutions(id);
  };

  const handleToggleKillSwitch = async () => {
    try {
      if (isKillSwitchActive) {
        await api.post("/api/automations/kill-switch/deactivate");
        setIsKillSwitchActive(false);
        toast({ title: "Automações reestabelecidas com sucesso.", type: "success" });
      } else {
        await api.post("/api/automations/kill-switch/activate");
        setIsKillSwitchActive(true);
        toast({ title: "Kill Switch Ativado! Todas as automações foram pausadas globalmente.", type: "warning" });
      }
    } catch {
      toast({ title: "Erro ao alternar Kill Switch", type: "error" });
    }
  };

  const handleRunAutomation = async (id: number) => {
    setRunningId(id);
    try {
      const res = await api.post<AutomationExecution>(`/api/automations/${id}/run?confirmed=true`);
      if (res.status === "completed") {
        toast({ title: "Automação executada com sucesso!", type: "success" });
      } else {
        toast({ title: `Falha na execução: ${res.error_message || "Erro desconhecido"}`, type: "error" });
      }
      loadExecutions(id);
    } catch {
      toast({ title: "Erro ao disparar automação", type: "error" });
    } finally {
      setRunningId(null);
    }
  };

  const handleToggleActive = async (id: number) => {
    try {
      await api.post(`/api/automations/${id}/toggle`);
      setAutomations(automations.map(a => a.id === id ? { ...a, is_active: !a.is_active } : a));
      toast({ title: "Status da rotina atualizado", type: "info" });
    } catch {
      toast({ title: "Erro ao alterar status da rotina", type: "error" });
    }
  };

  const handleUseTemplate = async (tpl: Template) => {
    try {
      await api.post("/api/automations/", {
        name: tpl.name,
        description: tpl.description,
        is_active: true,
        icon: "zap",
        triggers: [tpl.trigger],
        actions: tpl.actions,
      });
      toast({ title: `Template '${tpl.name}' ativado com sucesso!`, type: "success" });
      setActiveTab("automations");
      loadData();
    } catch {
      toast({ title: "Erro ao ativar template", type: "error" });
    }
  };

  const handleOpenCreate = () => {
    
    setName("");
    setDescription("");
    setTriggerType("SCHEDULE");
    setScheduleTime("08:00");
    setActionType("CREATE_NOTIFICATION");
    setAppName("vscode");
    setNotifTitle("Rotina Matinal");
    setNotifMsg("Bom dia! Suas tarefas do dia estão prontas.");
    setIsModalOpen(true);
  };

  const handleSaveAutomation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);

    let actionConfig: Record<string, any> = {};
    if (actionType === "CREATE_NOTIFICATION" || actionType === "SHOW_AGENT_MESSAGE") {
      actionConfig = { title: notifTitle, message: notifMsg };
    } else if (actionType === "OPEN_APPLICATION") {
      actionConfig = { app_name: appName };
    } else if (actionType === "START_STUDY_SESSION") {
      actionConfig = { duration_minutes: studyDuration, subject_id: 1 };
    }

    const payload = {
      name: name.trim(),
      description: description.trim() || null,
      is_active: true,
      icon: "zap",
      triggers: [
        {
          type: triggerType,
          config: triggerType === "SCHEDULE" ? { time: scheduleTime, days: [0, 1, 2, 3, 4] } : {},
        }
      ],
      actions: [
        {
          type: actionType,
          config: actionConfig,
          sort_order: 1,
          requires_confirmation: actionType === "OPEN_APPLICATION",
        }
      ],
    };

    try {
      await api.post("/api/automations/", payload);
      toast({ title: "Nova rotina criada e ativada com sucesso!", type: "success" });
      setIsModalOpen(false);
      loadData();
    } catch {
      toast({ title: "Erro ao cadastrar automação", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await api.delete(`/api/automations/${deleteId}`);
      toast({ title: "Automação excluída", type: "info" });
      setDeleteId(null);
      loadData();
    } catch {
      toast({ title: "Erro ao excluir automação", type: "error" });
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-surface-800/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Automações & Rotinas</h1>
          <p className="text-sm text-surface-400">
            Crie rotinas inteligentes de produtividade, abertura de aplicativos e notificações locais sem programar.
          </p>
        </div>
        <div className="flex items-center gap-3 flex-wrap">
          {/* Kill Switch Toggle */}
          <Button
            variant="outline"
            size="sm"
            onClick={handleToggleKillSwitch}
            className={`gap-1.5 text-xs font-semibold ${
              isKillSwitchActive
                ? "bg-red-500/20 text-red-400 border-red-500/40 hover:bg-red-500/30"
                : "border-surface-700 text-surface-400 hover:text-white"
            }`}
          >
            <Power className="w-3.5 h-3.5" />
            {isKillSwitchActive ? "Kill Switch Ativo (Pausado)" : "Pausar Todas as Rotinas"}
          </Button>

          <Button onClick={handleOpenCreate} className="gap-2 shrink-0">
            <Plus className="w-4 h-4" />
            Nova Automação
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-800/60 pb-3">
        {[
          { key: "automations", label: "Minhas Rotinas", icon: Zap },
          { key: "templates", label: "Rotinas Pré-Configuradas", icon: Sparkles },
          { key: "executions", label: "Histórico & Auditoria", icon: Layers },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                activeTab === tab.key
                  ? "bg-accent-500/20 text-accent-400 border border-accent-500/30 font-semibold"
                  : "text-surface-400 hover:text-surface-200 hover:bg-surface-800/60"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Content */}
      {isLoading ? (
        <LoadingState message="Carregando rotinas de automação..." />
      ) : activeTab === "automations" ? (
        <div>
          {automations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
              <div className="p-4 rounded-full bg-surface-800/50 mb-4 text-surface-500">
                <Zap className="w-10 h-10" />
              </div>
              <h3 className="text-base font-semibold text-surface-200 mb-1">
                Nenhuma rotina cadastrada
              </h3>
              <p className="text-xs text-surface-400 max-w-sm mb-5">
                Automatize a abertura de programas de desenvolvimento, notificações de estudo ou sincronização de e-mails.
              </p>
              <div className="flex items-center gap-3">
                <Button onClick={() => setActiveTab("templates")} variant="outline" size="sm" className="gap-1.5">
                  <Sparkles className="w-4 h-4" />
                  Ver Templates Prontos
                </Button>
                <Button onClick={handleOpenCreate} size="sm" className="gap-1.5">
                  <Plus className="w-4 h-4" />
                  Criar Nova Rotina
                </Button>
              </div>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {automations.map((auto) => {
                const isRunning = runningId === auto.id;
                const trig = auto.triggers?.[0];
                return (
                  <div
                    key={auto.id}
                    className={`glass-card p-5 flex flex-col justify-between hover:border-surface-600 transition-all space-y-4 ${
                      !auto.is_active ? "opacity-60" : ""
                    }`}
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <div className={`p-2 rounded-lg ${auto.is_active ? "bg-yellow-500/10 text-yellow-400" : "bg-surface-800 text-surface-500"}`}>
                            <Zap className="w-4 h-4" />
                          </div>
                          <div>
                            <h3 className="text-base font-bold text-white tracking-tight">{auto.name}</h3>
                            <span className="text-[11px] text-surface-400 font-mono">
                              {trig?.type === "SCHEDULE" ? `Agendado: ${trig.config?.time || "08:00"}` : "Disparo Manual"}
                            </span>
                          </div>
                        </div>

                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleToggleActive(auto.id)}
                            title={auto.is_active ? "Pausar rotina" : "Ativar rotina"}
                            className="p-1 text-surface-400 hover:text-white rounded transition-colors cursor-pointer text-xs"
                          >
                            {auto.is_active ? "Pausar" : "Ativar"}
                          </button>
                          <button
                            onClick={() => setDeleteId(auto.id)}
                            className="p-1 text-surface-500 hover:text-red-400 rounded transition-colors cursor-pointer"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>

                      {auto.description && (
                        <p className="text-xs text-surface-300 mt-2 line-clamp-2 leading-relaxed">
                          {auto.description}
                        </p>
                      )}

                      {auto.actions && auto.actions.length > 0 && (
                        <div className="mt-3 space-y-1">
                          {auto.actions.map((act, i) => (
                            <div key={i} className="text-[11px] text-surface-400 flex items-center gap-1.5">
                              <span className="w-1.5 h-1.5 rounded-full bg-accent-400" />
                              <span className="font-mono text-surface-300">{act.type}</span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-surface-800/60">
                      <div className="flex items-center gap-1.5 text-xs text-green-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span className="text-[11px] text-surface-400">
                          {auto.is_active ? "Ativa" : "Pausada"}
                        </span>
                      </div>

                      <Button
                        size="sm"
                        isLoading={isRunning}
                        disabled={isKillSwitchActive}
                        onClick={() => handleRunAutomation(auto.id)}
                        className="gap-1.5 shadow-md shadow-accent-600/20"
                      >
                        <Play className="w-3.5 h-3.5" />
                        Executar Agora
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : activeTab === "templates" ? (
        /* Templates Tab */
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          {templates.map((tpl) => (
            <div key={tpl.id} className="glass-card p-5 flex flex-col justify-between space-y-4 hover:border-accent-500/40 transition-all">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <div className="p-2 rounded-lg bg-accent-500/10 text-accent-400">
                    <Sparkles className="w-4 h-4" />
                  </div>
                  <Badge variant="outline" className="text-[10px] text-accent-400 border-accent-500/30">
                    Risco: {tpl.risk_level}
                  </Badge>
                </div>
                <h3 className="text-base font-bold text-white tracking-tight">{tpl.name}</h3>
                <p className="text-xs text-surface-400 leading-relaxed">{tpl.description}</p>
                <div className="pt-2 space-y-1">
                  {tpl.actions.map((act, i) => (
                    <div key={i} className="text-[11px] text-surface-300 flex items-center gap-1.5">
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span>{act.type}</span>
                    </div>
                  ))}
                </div>
              </div>

              <Button onClick={() => handleUseTemplate(tpl)} className="w-full gap-1.5 text-xs">
                <Plus className="w-3.5 h-3.5" />
                Ativar este Template
              </Button>
            </div>
          ))}
        </div>
      ) : (
        /* Executions Tab */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="glass-card p-4 space-y-2">
            <h3 className="text-xs font-bold text-surface-400 uppercase tracking-wider mb-2">
              Selecione a Rotina
            </h3>
            {automations.map((a) => (
              <button
                key={a.id}
                onClick={() => handleSelectAutomation(a.id)}
                className={`w-full text-left p-2.5 rounded-lg text-xs font-medium transition-all flex items-center justify-between cursor-pointer ${
                  selectedAutoId === a.id
                    ? "bg-accent-500/20 text-accent-400 border border-accent-500/30"
                    : "text-surface-300 hover:bg-surface-800/60 hover:text-white"
                }`}
              >
                <span className="truncate">{a.name}</span>
                <Terminal className="w-3.5 h-3.5 shrink-0 opacity-40" />
              </button>
            ))}
          </div>

          <div className="lg:col-span-2 glass-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-surface-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-accent-400" />
                Histórico & Auditoria de Execuções
              </h3>
              {selectedAutoId && (
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => loadExecutions(selectedAutoId)}
                  className="h-7 px-2 text-xs gap-1 text-surface-400 hover:text-white"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                  Atualizar
                </Button>
              )}
            </div>

            {executions.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-surface-500">
                <FileText className="w-8 h-8 mb-2 opacity-30" />
                <p className="text-xs">Nenhuma execução registrada para esta rotina.</p>
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[460px] overflow-y-auto pr-1">
                {executions.map((exec) => {
                  const isSuccess = exec.status === "completed";
                  return (
                    <div
                      key={exec.id}
                      className="p-3.5 rounded-lg border border-surface-800 bg-surface-900/60 space-y-2"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          {isSuccess ? (
                            <CheckCircle2 className="w-4 h-4 text-green-400" />
                          ) : (
                            <XCircle className="w-4 h-4 text-red-400" />
                          )}
                          <span className="text-xs font-bold text-white capitalize">
                            Status: {exec.status === "completed" ? "Concluído" : "Falhou"}
                          </span>
                        </div>
                        <span className="text-[11px] text-surface-400">
                          {formatDate(exec.started_at)}
                        </span>
                      </div>

                      {exec.log && (
                        <pre className="text-[11px] font-mono bg-surface-950/80 p-2.5 rounded border border-surface-800/80 text-surface-300 overflow-x-auto whitespace-pre-wrap">
                          {exec.log}
                        </pre>
                      )}

                      {exec.error_message && (
                        <p className="text-xs text-red-400 bg-red-500/10 p-2 rounded border border-red-500/20">
                          Erro: {exec.error_message}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Automation Wizard Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Assistente de Criação de Rotina"
        size="md"
      >
        <form onSubmit={handleSaveAutomation} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-surface-300 mb-1.5 block">1. Nome da Rotina *</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Rotina da Manhã, Iniciar Estudos..."
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Descrição</label>
            <Input
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="O que esta automação realiza..."
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-surface-300 mb-1.5 block">2. Quando disparar?</label>
              <select
                value={triggerType}
                onChange={(e) => setTriggerType(e.target.value as any)}
                className="w-full rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value="SCHEDULE">Horário Agendado (Diário)</option>
                <option value="MANUAL">Disparo Manual</option>
                <option value="APP_START">Ao Iniciar o Resolva</option>
              </select>
            </div>

            {triggerType === "SCHEDULE" && (
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Horário (HH:MM)</label>
                <Input
                  type="time"
                  value={scheduleTime}
                  onChange={(e) => setScheduleTime(e.target.value)}
                  required
                />
              </div>
            )}
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-300 mb-1.5 block">3. O que executar?</label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value as any)}
              className="w-full rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-500"
            >
              <option value="CREATE_NOTIFICATION">Enviar Notificação do Sistema</option>
              <option value="SHOW_AGENT_MESSAGE">Exibir Mensagem do Resolva Agent</option>
              <option value="OPEN_APPLICATION">Abrir Aplicativo Autorizado (Windows)</option>
              <option value="START_STUDY_SESSION">Iniciar Sessão de Estudo / Pomodoro</option>
            </select>
          </div>

          {actionType === "OPEN_APPLICATION" && (
            <div className="space-y-2 p-3 rounded-lg border border-surface-800 bg-surface-900/40">
              <label className="text-xs font-semibold text-surface-300 mb-1 block">Aplicativo da Whitelist</label>
              <select
                value={appName}
                onChange={(e) => setAppName(e.target.value)}
                className="w-full rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value="vscode">VS Code (Visual Studio Code)</option>
                <option value="chrome">Google Chrome</option>
                <option value="discord">Discord</option>
                <option value="spotify">Spotify</option>
                <option value="notepad">Bloco de Notas</option>
              </select>
            </div>
          )}

          {actionType === "START_STUDY_SESSION" && (
            <div className="p-3 rounded-lg border border-surface-800 bg-surface-900/40">
              <label className="text-xs font-semibold text-surface-300 mb-1 block">Duração em Minutos</label>
              <Input
                type="number"
                min={5}
                max={120}
                value={studyDuration}
                onChange={(e) => setStudyDuration(Number(e.target.value))}
                required
              />
            </div>
          )}

          {(actionType === "CREATE_NOTIFICATION" || actionType === "SHOW_AGENT_MESSAGE") && (
            <div className="space-y-3 p-3 rounded-lg border border-surface-800 bg-surface-900/40">
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1 block">Título</label>
                <Input value={notifTitle} onChange={(e) => setNotifTitle(e.target.value)} required />
              </div>
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1 block">Mensagem</label>
                <Input value={notifMsg} onChange={(e) => setNotifMsg(e.target.value)} required />
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-3 border-t border-surface-800">
            <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Ativar Automação
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteId !== null}
        onClose={() => setDeleteId(null)}
        onConfirm={handleDelete}
        title="Excluir Automação"
        message="Tem certeza que deseja excluir esta rotina de automação? O histórico associado será preservado."
        confirmLabel="Excluir"
        variant="destructive"
      />
    </div>
  );
}

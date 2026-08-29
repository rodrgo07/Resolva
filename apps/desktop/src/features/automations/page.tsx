import { useState, useEffect } from "react";
import { 
  Zap, Play, Plus, Trash2, CheckCircle2, XCircle, 
  Clock, ShieldCheck, Terminal, Layers, RefreshCw, FileText
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { ConfirmationDialog } from "@/components/shared/confirmation-dialog";
import { LoadingState } from "@/components/shared/loading-state";
import { formatDate } from "@/lib/utils";

interface Automation {
  id: number;
  name: string;
  description: string | null;
  is_active: boolean;
  icon: string | null;
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

export function AutomationsPage() {
  const [automations, setAutomations] = useState<Automation[]>([]);
  const [executions, setExecutions] = useState<AutomationExecution[]>([]);
  const [selectedAutoId, setSelectedAutoId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [runningId, setRunningId] = useState<number | null>(null);

  // Tabs
  const [activeTab, setActiveTab] = useState<"automations" | "executions">("automations");

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // Form states
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [actionType, setActionType] = useState<"open_application" | "send_notification">("open_application");
  const [appName, setAppName] = useState("code");
  const [appPath, setAppPath] = useState("C:\\Users\\thega\\Documents\\Resolva");
  const [notifTitle, setNotifTitle] = useState("Rotina Executada");
  const [notifMsg, setNotifMsg] = useState("Automação concluída com sucesso!");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { toast } = useToast();

  const loadData = async () => {
    try {
      setIsLoading(true);
      const autos = await api.get<Automation[]>("/api/automations/");
      setAutomations(autos || []);
      if (autos && autos.length > 0 && selectedAutoId === null) {
        setSelectedAutoId(autos[0].id);
        loadExecutions(autos[0].id);
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

  const handleRunAutomation = async (id: number) => {
    setRunningId(id);
    try {
      const res = await api.post<AutomationExecution>(`/api/automations/${id}/run`);
      if (res.status === "completed") {
        toast({ title: "Automação executada com sucesso!", type: "success" });
      } else {
        toast({ title: "Falha na execução da automação", type: "error" });
      }
      loadExecutions(id);
    } catch {
      toast({ title: "Erro ao disparar automação", type: "error" });
    } finally {
      setRunningId(null);
    }
  };

  const handleOpenCreate = () => {
    setName("");
    setDescription("");
    setActionType("open_application");
    setAppName("code");
    setAppPath("C:\\Users\\thega\\Documents\\Resolva");
    setNotifTitle("Rotina Executada");
    setNotifMsg("Automação concluída com sucesso!");
    setIsModalOpen(true);
  };

  const handleSaveAutomation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    setIsSubmitting(true);
    const actionConfig = actionType === "open_application"
      ? { app_name: appName, path: appPath }
      : { title: notifTitle, message: notifMsg };

    const payload = {
      name: name.trim(),
      description: description.trim() || null,
      is_active: true,
      icon: "zap",
      triggers: [{ type: "manual", config: { description: "Disparo manual" } }],
      actions: [
        {
          type: actionType,
          config: actionConfig,
          sort_order: 1,
          requires_confirmation: false,
        }
      ],
    };

    try {
      await api.post("/api/automations/", payload);
      toast({ title: "Automação criada com sucesso", type: "success" });
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
          <h1 className="text-2xl font-bold text-white tracking-tight">Automações</h1>
          <p className="text-sm text-surface-400">
            Crie e execute fluxos e comandos locais de forma rápida e segura.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={handleOpenCreate} className="gap-2 shrink-0">
            <Plus className="w-4 h-4" />
            Nova Automação
          </Button>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="flex items-center gap-2 border-b border-surface-800/60 pb-3">
        {[
          { key: "automations", label: "Rotinas Cadastradas", icon: Zap },
          { key: "executions", label: "Histórico & Auditoria", icon: Layers },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`flex items-center gap-2 px-3.5 py-1.5 rounded-lg text-xs font-medium transition-all cursor-pointer ${
                activeTab === tab.key
                  ? "bg-accent-500/20 text-accent-400 border border-accent-500/30"
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
                Nenhuma rotina configurada
              </h3>
              <p className="text-xs text-surface-400 max-w-sm mb-5">
                Automatize tarefas repetitivas, abertura de programas e notificações.
              </p>
              <Button onClick={handleOpenCreate} size="sm" className="gap-1.5">
                <Plus className="w-4 h-4" />
                Criar Primeira Rotina
              </Button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {automations.map((auto) => {
                const isRunning = runningId === auto.id;
                return (
                  <div
                    key={auto.id}
                    className="glass-card p-5 flex flex-col justify-between hover:border-surface-600 transition-all space-y-4"
                  >
                    <div>
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2.5">
                          <div className="p-2 rounded-lg bg-yellow-500/10 text-yellow-400">
                            <Zap className="w-4 h-4" />
                          </div>
                          <div>
                            <h3 className="text-base font-bold text-white tracking-tight">{auto.name}</h3>
                            <span className="text-[11px] text-surface-500">Disparo Manual</span>
                          </div>
                        </div>

                        <button
                          onClick={() => setDeleteId(auto.id)}
                          className="p-1 text-surface-500 hover:text-red-400 rounded transition-colors cursor-pointer"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>

                      {auto.description && (
                        <p className="text-xs text-surface-300 mt-2 line-clamp-2 leading-relaxed">
                          {auto.description}
                        </p>
                      )}
                    </div>

                    <div className="flex items-center justify-between pt-3 border-t border-surface-800/60">
                      <div className="flex items-center gap-1.5 text-xs text-green-400">
                        <ShieldCheck className="w-3.5 h-3.5" />
                        <span className="text-[11px] text-surface-400">Seguro</span>
                      </div>

                      <Button
                        size="sm"
                        isLoading={isRunning}
                        onClick={() => handleRunAutomation(auto.id)}
                        className="gap-1.5 shadow-md shadow-accent-600/20"
                      >
                        <Play className="w-3.5 h-3.5" />
                        Executar
                      </Button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      ) : (
        /* Executions & Audit Log Tab */
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sidebar list of automations */}
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

          {/* Executions timeline & logs */}
          <div className="lg:col-span-2 glass-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-surface-800 pb-3">
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                <Clock className="w-4 h-4 text-accent-400" />
                Histórico de Execuções
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

      {/* Create Automation Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Nova Rotina de Automação"
        size="md"
      >
        <form onSubmit={handleSaveAutomation} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Nome da Rotina *</label>
            <Input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ex: Abrir Ambiente de Trabalho, Modo Foco..."
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Descrição</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="O que esta automação realiza..."
              className="w-full rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm text-white placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-accent-500"
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Tipo de Ação</label>
            <select
              value={actionType}
              onChange={(e) => setActionType(e.target.value as any)}
              className="w-full rounded-md border border-surface-700 bg-surface-800 px-3 py-2 text-sm text-white focus:outline-none focus:ring-2 focus:ring-accent-500"
            >
              <option value="open_application">Abrir Aplicativo / Diretório</option>
              <option value="send_notification">Disparar Notificação do Sistema</option>
            </select>
          </div>

          {actionType === "open_application" ? (
            <div className="space-y-3 p-3 rounded-lg border border-surface-800 bg-surface-900/40">
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Nome do App / Comando</label>
                <Input
                  value={appName}
                  onChange={(e) => setAppName(e.target.value)}
                  placeholder="code, notepad, chrome..."
                  required
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Caminho ou Argumento</label>
                <Input
                  value={appPath}
                  onChange={(e) => setAppPath(e.target.value)}
                  placeholder="C:\Users\...\Projeto"
                />
              </div>
            </div>
          ) : (
            <div className="space-y-3 p-3 rounded-lg border border-surface-800 bg-surface-900/40">
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Título da Notificação</label>
                <Input
                  value={notifTitle}
                  onChange={(e) => setNotifTitle(e.target.value)}
                  placeholder="Ex: Lembrete Importante"
                  required
                />
              </div>
              <div>
                <label className="text-xs font-semibold text-surface-300 mb-1.5 block">Mensagem</label>
                <Input
                  value={notifMsg}
                  onChange={(e) => setNotifMsg(e.target.value)}
                  placeholder="Ex: Hora da reunião diária!"
                  required
                />
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-3 border-t border-surface-800">
            <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Salvar Automação
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

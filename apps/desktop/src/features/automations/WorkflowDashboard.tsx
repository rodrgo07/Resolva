import { useState, useEffect } from "react";
import { GitBranch, Play, Plus } from "lucide-react";
import { api } from "@/lib/api-client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { LoadingState } from "@/components/shared/loading-state";

interface WorkflowStep {
  name: string;
  action_type: string;
  parameters: Record<string, any>;
  timeout_seconds?: number;
  requires_confirmation?: boolean;
}

interface Workflow {
  id: number;
  workflow_id: string;
  name: string;
  description: string | null;
  enabled: boolean;
  status: string;
  safety_level: string;
  execution_policy: string;
  trigger_config: Record<string, any>;
  condition_config?: Record<string, any> | null;
  steps: WorkflowStep[];
  created_at: string;
}

interface WorkflowTemplate {
  template_id: string;
  name: string;
  description: string;
  category: string;
  safety_level: string;
  trigger_config: Record<string, any>;
  steps: WorkflowStep[];
}

export function WorkflowDashboard() {
  const { toast } = useToast();
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [templates, setTemplates] = useState<WorkflowTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTab, setSelectedTab] = useState<"ACTIVE" | "TEMPLATES">("ACTIVE");

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [newName, setNewName] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newActionType, setNewActionType] = useState("SHOW_NOTIFICATION");
  const [newStepName, setNewStepName] = useState("Notificar Conclusão");

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [wfs, tpls] = await Promise.all([
        api.get<Workflow[]>("/api/workflows"),
        api.get<WorkflowTemplate[]>("/api/workflows/catalog/templates")
      ]);
      setWorkflows(wfs || []);
      setTemplates(tpls || []);
    } catch {
      toast({ title: "Erro", description: "Falha ao carregar workflows.", type: "error" });
    } finally {
      setLoading(false);
    }
  };


  useEffect(() => {
    fetchAll();
  }, []);

  const handleToggle = async (wf: Workflow) => {
    const action = wf.enabled ? "pause" : "activate";
    try {
      await api.post("/api/workflows/" + wf.workflow_id + "/" + action, {});
      toast({ title: "Status Atualizado", description: "Workflow " + wf.name + (wf.enabled ? " pausado." : " ativado."), type: "success" });
      fetchAll();
    } catch {
      toast({ title: "Erro", description: "Falha ao alterar estado do workflow.", type: "error" });
    }
  };

  const handleTestDryRun = async (wf: Workflow) => {
    try {
      const res = await api.post<any>("/api/workflows/" + wf.workflow_id + "/test", {
        device_id: "DESKTOP-MAIN"
      });
      toast({
        title: "Dry Run Concluído",
        description: "Simulação executada com sucesso. Status: " + res.status,
        type: "success"
      });
    } catch {
      toast({ title: "Erro", description: "Falha ao simular workflow.", type: "error" });
    }
  };

  const handleCreateFromTemplate = async (tpl: WorkflowTemplate) => {
    try {
      await api.post("/api/workflows", {
        name: tpl.name,
        description: tpl.description,
        safety_level: tpl.safety_level,
        trigger_config: tpl.trigger_config,
        steps: tpl.steps
      });
      toast({ title: "Template Ativado", description: "Workflow '" + tpl.name + "' criado com sucesso!", type: "success" });
      setSelectedTab("ACTIVE");
      fetchAll();
    } catch {
      toast({ title: "Erro", description: "Falha ao criar workflow do template.", type: "error" });
    }
  };

  const handleCreateCustom = async () => {
    if (!newName.trim()) return;
    try {
      await api.post("/api/workflows", {
        name: newName,
        description: newDesc,
        safety_level: "AUTO_LOW_RISK",
        trigger_config: { type: "MANUAL" },
        steps: [
          {
            name: newStepName,
            action_type: newActionType,
            parameters: newActionType === "SHOW_NOTIFICATION" ? { title: newName, message: "Executado com sucesso." } : {}
          }
        ]
      });
      toast({ title: "Workflow Criado", description: "Workflow '" + newName + "' configurado com sucesso.", type: "success" });
      setIsCreateOpen(false);
      setNewName("");
      setNewDesc("");
      fetchAll();
    } catch {
      toast({ title: "Erro", description: "Falha ao criar workflow customizado.", type: "error" });
    }
  };

  if (loading) return <LoadingState message="Carregando Workflow Engine..." />;


  const activeTabClass = (tab: "ACTIVE" | "TEMPLATES") => {
    return selectedTab === tab ? "bg-accent text-text-primary" : "text-text-secondary hover:text-text-primary";
  };

  return (
    <div className="space-y-6 animate-fade-in p-2">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <h2 className="text-lg font-bold text-text-primary flex items-center gap-2">
            <GitBranch className="w-5 h-5 text-accent-light" />
            Workflow Engine & Intelligence
          </h2>
          <p className="text-xs text-text-secondary mt-1">
            Automações declarativas com permissionamento estrito, simulação Dry Run e auditoria.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <div className="bg-surface border border-border p-1 rounded-xl flex gap-1 text-xs">
            <button
              onClick={() => setSelectedTab("ACTIVE")}
              className={"px-3 py-1.5 rounded-lg font-medium transition-colors " + activeTabClass("ACTIVE")}
            >
              Meus Workflows ({workflows.length})
            </button>
            <button
              onClick={() => setSelectedTab("TEMPLATES")}
              className={"px-3 py-1.5 rounded-lg font-medium transition-colors " + activeTabClass("TEMPLATES")}
            >
              Templates Homologados ({templates.length})
            </button>
          </div>

          <Button size="sm" onClick={() => setIsCreateOpen(true)} className="gap-1.5 bg-accent hover:bg-accent text-xs">
            <Plus className="w-4 h-4" /> Novo Workflow
          </Button>
        </div>
      </div>

      {selectedTab === "ACTIVE" && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.map((wf) => (
            <div key={wf.workflow_id} className="glass-card p-4 rounded-xl border border-border bg-background/60 space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-bold text-text-primary flex items-center gap-2">
                    {wf.name}
                    <Badge variant={wf.enabled ? "success" : "secondary"} className="text-[10px]">
                      {wf.enabled ? "ATIVO" : "PAUSADO"}
                    </Badge>
                  </h3>
                  {wf.description && <p className="text-xs text-text-secondary mt-0.5">{wf.description}</p>}
                </div>

                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleToggle(wf)}
                  className="h-7 text-xs border-border text-text-secondary hover:text-text-primary"
                >
                  {wf.enabled ? "Pausar" : "Ativar"}
                </Button>
              </div>

              <div className="p-2.5 rounded-lg bg-surface/80 border border-border/80 space-y-1.5 text-xs">
                <span className="text-[10px] font-bold text-text-secondary uppercase tracking-wider">
                  Etapas ({wf.steps?.length || 0}):
                </span>
                {wf.steps?.map((step, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-text-secondary">
                    <span className="w-4 h-4 rounded-full bg-accent/20 text-accent-light text-[10px] flex items-center justify-center font-bold">
                      {idx + 1}
                    </span>
                    <span>{step.name}</span>
                    <span className="text-[10px] font-mono text-text-secondary">({step.action_type})</span>
                  </div>
                ))}
              </div>

              <div className="flex items-center justify-end gap-2 pt-1 border-t border-border/60">
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleTestDryRun(wf)}
                  className="h-7 text-xs text-accent-light hover:text-accent-300 hover:bg-accent/10 gap-1"
                >
                  <Play className="w-3 h-3" /> Simular (Dry Run)
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}

      {selectedTab === "TEMPLATES" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map((tpl) => (
            <div key={tpl.template_id} className="glass-card p-4 rounded-xl border border-border bg-background/60 flex flex-col justify-between space-y-3">
              <div className="space-y-1.5">
                <div className="flex items-center justify-between">
                  <Badge variant="outline" className="text-[10px] text-accent-light border-accent/30">
                    {tpl.category}
                  </Badge>
                  <span className="text-[10px] text-text-secondary font-mono">{tpl.steps.length} etapas</span>
                </div>
                <h4 className="text-sm font-bold text-text-primary">{tpl.name}</h4>
                <p className="text-xs text-text-secondary">{tpl.description}</p>
              </div>

              <Button
                size="sm"
                onClick={() => handleCreateFromTemplate(tpl)}
                className="w-full text-xs bg-surface-elevated hover:bg-accent hover:text-text-primary text-text-primary transition-colors"
              >
                Ativar este Template
              </Button>
            </div>
          ))}
        </div>
      )}

      <Modal isOpen={isCreateOpen} onClose={() => setIsCreateOpen(false)} title="Criar Novo Workflow">
        <div className="space-y-4 text-xs text-text-secondary">
          <div>
            <label className="block text-text-secondary mb-1 font-medium">Nome do Workflow</label>
            <Input value={newName} onChange={(e) => setNewName(e.target.value)} placeholder="Ex: Preparação para Estudos" />
          </div>

          <div>
            <label className="block text-text-secondary mb-1 font-medium">Descrição</label>
            <Input value={newDesc} onChange={(e) => setNewDesc(e.target.value)} placeholder="Objetivo desta automação..." />
          </div>

          <div className="p-3 rounded-xl bg-surface/80 border border-border space-y-3">
            <span className="font-bold text-accent-light">Etapa Inicial (Catálogo Homologado)</span>
            <div>
              <label className="block text-text-secondary mb-1 font-medium">Nome da Etapa</label>
              <Input value={newStepName} onChange={(e) => setNewStepName(e.target.value)} />
            </div>

            <div>
              <label className="block text-text-secondary mb-1 font-medium">Ação Homologada</label>
              <select
                value={newActionType}
                onChange={(e) => setNewActionType(e.target.value)}
                className="w-full bg-background border border-border rounded-lg p-2 text-text-primary text-xs outline-none"
              >
                <option value="SHOW_NOTIFICATION">SHOW_NOTIFICATION (Notificação)</option>
                <option value="START_POMODORO">START_POMODORO (Iniciar Foco)</option>
                <option value="CREATE_TASK">CREATE_TASK (Criar Tarefa)</option>
                <option value="CREATE_STUDY_SESSION">CREATE_STUDY_SESSION (Registrar Estudo)</option>
                <option value="GET_TODAY_CONTEXT">GET_TODAY_CONTEXT (Contexto Matinal)</option>
                <option value="SYNC_NOW">SYNC_NOW (Sincronizar Fila)</option>
                <option value="CREATE_BACKUP">CREATE_BACKUP (Backup SQLite)</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-2 pt-2">
            <Button variant="ghost" size="sm" onClick={() => setIsCreateOpen(false)}>Cancelar</Button>
            <Button size="sm" onClick={handleCreateCustom} className="bg-accent hover:bg-accent text-text-primary">Criar Workflow</Button>
          </div>
        </div>
      </Modal>
    </div>
  );
}

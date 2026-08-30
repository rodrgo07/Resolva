import { useState, useEffect, useMemo } from "react";
import { 
  Plus, Filter, CheckSquare, 
  Trash2, Edit3, Copy, CheckCircle2, Circle, 
  Calendar, Tag, ChevronDown, ChevronRight
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

type Priority = "baixa" | "media" | "alta" | "urgente";
type TaskStatus = "pendente" | "em_andamento" | "concluida" | "arquivada";

interface Subtask {
  id: number;
  task_id: number;
  title: string;
  completed: boolean;
  sort_order: number;
}

interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: Priority;
  status: TaskStatus;
  category: string | null;
  due_date: string | null;
  due_time: string | null;
  recurrence: string | null;
  tags: { tags?: string[] } | null;
  subtasks: Subtask[];
  created_at: string;
}

export function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [filter, setFilter] = useState<"all" | "today" | "overdue" | "high" | "completed">("all");
  
  // Modal states
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deleteTaskId, setDeleteTaskId] = useState<number | null>(null);
  const [expandedTaskId, setExpandedTaskId] = useState<number | null>(null);

  // Form states
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<Priority>("media");
  const [category, setCategory] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [tagsInput, setTagsInput] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { toast } = useToast();

  const loadTasks = async () => {
    try {
      setIsLoading(true);
      const data = await api.get<Task[]>("/api/tasks/");
      setTasks(data || []);
    } catch {
      toast({ title: "Erro ao carregar tarefas", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadTasks();
  }, []);

  const handleOpenCreate = () => {
    setEditingTask(null);
    setTitle("");
    setDescription("");
    setPriority("media");
    setCategory("");
    setDueDate(new Date().toISOString().split("T")[0]);
    setTagsInput("");
    setIsFormOpen(true);
  };

  const handleOpenEdit = (task: Task) => {
    setEditingTask(task);
    setTitle(task.title);
    setDescription(task.description || "");
    setPriority(task.priority);
    setCategory(task.category || "");
    setDueDate(task.due_date ? task.due_date.split("T")[0] : "");
    setTagsInput(task.tags?.tags ? task.tags.tags.join(", ") : "");
    setIsFormOpen(true);
  };

  const handleSaveTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    const tagsArray = tagsInput.split(",").map(t => t.trim()).filter(Boolean);
    const payload = {
      title,
      description: description || null,
      priority,
      category: category || null,
      due_date: dueDate || null,
      tags: tagsArray.length > 0 ? { tags: tagsArray } : null,
    };

    try {
      if (editingTask) {
        await api.put(`/api/tasks/${editingTask.id}`, payload);
        toast({ title: "Tarefa atualizada com sucesso", type: "success" });
      } else {
        await api.post("/api/tasks/", payload);
        toast({ title: "Tarefa criada com sucesso", type: "success" });
      }
      setIsFormOpen(false);
      loadTasks();
    } catch {
      toast({ title: "Erro ao salvar tarefa", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleToggleComplete = async (task: Task) => {
    try {
      if (task.status === "concluida") {
        await api.put(`/api/tasks/${task.id}`, { status: "pendente" });
      } else {
        await api.post(`/api/tasks/${task.id}/complete`);
      }
      loadTasks();
    } catch {
      toast({ title: "Erro ao alterar status da tarefa", type: "error" });
    }
  };

  const handleDuplicate = async (taskId: number) => {
    try {
      await api.post(`/api/tasks/${taskId}/duplicate`);
      toast({ title: "Tarefa duplicada com sucesso", type: "success" });
      loadTasks();
    } catch {
      toast({ title: "Erro ao duplicar tarefa", type: "error" });
    }
  };

  const handleDelete = async () => {
    if (!deleteTaskId) return;
    try {
      await api.delete(`/api/tasks/${deleteTaskId}`);
      toast({ title: "Tarefa excluída", type: "info" });
      setDeleteTaskId(null);
      loadTasks();
    } catch {
      toast({ title: "Erro ao excluir tarefa", type: "error" });
    }
  };

  const filteredTasks = useMemo(() => {
    const todayStr = new Date().toISOString().split("T")[0];
    return tasks.filter((t) => {
      if (filter === "completed") return t.status === "concluida";
      if (filter === "high") return t.priority === "alta" || t.priority === "urgente";
      if (filter === "today") return t.due_date?.startsWith(todayStr);
      if (filter === "overdue") {
        return t.status !== "concluida" && t.due_date && t.due_date < todayStr;
      }
      return true;
    });
  }, [tasks, filter]);

  const getPriorityBadge = (p: Priority) => {
    switch (p) {
      case "urgente":
        return <Badge variant="error">Urgente</Badge>;
      case "alta":
        return <Badge variant="warning">Alta</Badge>;
      case "media":
        return <Badge variant="default">Média</Badge>;
      case "baixa":
        return <Badge variant="secondary">Baixa</Badge>;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Tarefas</h1>
          <p className="text-sm text-text-secondary">
            Gerencie seus compromissos, subtarefas e prioridades do dia a dia.
          </p>
        </div>
        <Button onClick={handleOpenCreate} className="gap-2 shrink-0">
          <Plus className="w-4 h-4" />
          Nova Tarefa
        </Button>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        <Filter className="w-4 h-4 text-text-muted shrink-0 ml-1" />
        {[
          { key: "all", label: "Todas" },
          { key: "today", label: "Hoje" },
          { key: "overdue", label: "Atrasadas" },
          { key: "high", label: "Alta Prioridade" },
          { key: "completed", label: "Concluídas" },
        ].map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key as any)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap cursor-pointer ${
              filter === f.key
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
        <LoadingState message="Carregando tarefas..." />
      ) : filteredTasks.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 text-center glass-card border-dashed">
          <div className="p-4 rounded-full bg-surface-elevated/50 mb-4 text-text-muted">
            <CheckSquare className="w-10 h-10" />
          </div>
          <h3 className="text-base font-semibold text-text-primary mb-1">
            Nenhuma tarefa encontrada
          </h3>
          <p className="text-xs text-text-secondary max-w-sm mb-5">
            Não há afazeres para a categoria ou filtro selecionado.
          </p>
          <Button onClick={handleOpenCreate} size="sm" className="gap-1.5">
            <Plus className="w-4 h-4" />
            Criar Tarefa
          </Button>
        </div>
      ) : (
        <div className="space-y-3">
          {filteredTasks.map((task) => {
            const isCompleted = task.status === "concluida";
            const isExpanded = expandedTaskId === task.id;

            return (
              <div
                key={task.id}
                className={`glass-card p-4 transition-all duration-200 ${
                  isCompleted ? "opacity-60 bg-background/40" : "hover:border-border-strong"
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex items-start gap-3 flex-1 min-w-0">
                    <button
                      onClick={() => handleToggleComplete(task)}
                      className="mt-0.5 text-text-secondary hover:text-accent-light transition-colors cursor-pointer shrink-0"
                    >
                      {isCompleted ? (
                        <CheckCircle2 className="w-5 h-5 text-success" />
                      ) : (
                        <Circle className="w-5 h-5" />
                      )}
                    </button>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={`text-sm font-semibold ${
                            isCompleted ? "line-through text-text-secondary" : "text-text-primary"
                          }`}
                        >
                          {task.title}
                        </span>
                        {getPriorityBadge(task.priority)}
                        {task.category && (
                          <Badge variant="outline" className="text-[10px] py-0 px-1.5 border-border">
                            {task.category}
                          </Badge>
                        )}
                      </div>

                      {task.description && (
                        <p className="text-xs text-text-secondary mt-1 line-clamp-2 leading-relaxed">
                          {task.description}
                        </p>
                      )}

                      <div className="flex items-center gap-4 mt-3 text-[11px] text-text-secondary flex-wrap">
                        {task.due_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="w-3.5 h-3.5 text-text-muted" />
                            {formatDate(task.due_date)}
                          </span>
                        )}
                        {task.tags?.tags && task.tags.tags.length > 0 && (
                          <span className="flex items-center gap-1">
                            <Tag className="w-3.5 h-3.5 text-text-muted" />
                            {task.tags.tags.join(", ")}
                          </span>
                        )}
                        {task.subtasks?.length > 0 && (
                          <button
                            onClick={() => setExpandedTaskId(isExpanded ? null : task.id)}
                            className="flex items-center gap-1 text-accent-light hover:text-accent-300 font-medium cursor-pointer"
                          >
                            {isExpanded ? <ChevronDown className="w-3.5 h-3.5" /> : <ChevronRight className="w-3.5 h-3.5" />}
                            {task.subtasks.filter(s => s.completed).length}/{task.subtasks.length} subtarefas
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center gap-1 shrink-0">
                    <button
                      onClick={() => handleDuplicate(task.id)}
                      title="Duplicar"
                      className="p-1.5 text-text-secondary hover:text-text-primary rounded-md hover:bg-surface-elevated transition-colors cursor-pointer"
                    >
                      <Copy className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleOpenEdit(task)}
                      title="Editar"
                      className="p-1.5 text-text-secondary hover:text-text-primary rounded-md hover:bg-surface-elevated transition-colors cursor-pointer"
                    >
                      <Edit3 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => setDeleteTaskId(task.id)}
                      title="Excluir"
                      className="p-1.5 text-text-secondary hover:text-error rounded-md hover:bg-surface-elevated transition-colors cursor-pointer"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Expanded Subtasks */}
                {isExpanded && task.subtasks?.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-border/60 pl-8 space-y-1.5">
                    {task.subtasks.map((sub) => (
                      <div key={sub.id} className="flex items-center gap-2 text-xs text-text-secondary">
                        {sub.completed ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-success" />
                        ) : (
                          <Circle className="w-3.5 h-3.5 text-text-muted" />
                        )}
                        <span className={sub.completed ? "line-through text-text-muted" : ""}>
                          {sub.title}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Create / Edit Modal */}
      <Modal
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        title={editingTask ? "Editar Tarefa" : "Nova Tarefa"}
        size="md"
      >
        <form onSubmit={handleSaveTask} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Título *</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Entregar relatório trimestral"
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Descrição</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              placeholder="Detalhes adicionais ou instruções..."
              className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-accent-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Prioridade</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value as Priority)}
                className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value="baixa">Baixa</option>
                <option value="media">Média</option>
                <option value="alta">Alta</option>
                <option value="urgente">Urgente</option>
              </select>
            </div>

            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Prazo (Data)</label>
              <Input
                type="date"
                value={dueDate}
                onChange={(e) => setDueDate(e.target.value)}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Categoria</label>
              <Input
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                placeholder="Ex: Trabalho, Estudos, Pessoal"
              />
            </div>

            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Tags (separadas por vírgula)</label>
              <Input
                value={tagsInput}
                onChange={(e) => setTagsInput(e.target.value)}
                placeholder="dev, urgente, relatorio"
              />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-3 border-t border-border">
            <Button variant="ghost" type="button" onClick={() => setIsFormOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              {editingTask ? "Salvar Alterações" : "Criar Tarefa"}
            </Button>
          </div>
        </form>
      </Modal>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteTaskId !== null}
        onClose={() => setDeleteTaskId(null)}
        onConfirm={handleDelete}
        title="Excluir Tarefa"
        message="Tem certeza que deseja excluir esta tarefa? Esta ação não poderá ser desfeita."
        confirmLabel="Excluir"
        variant="destructive"
      />
    </div>
  );
}

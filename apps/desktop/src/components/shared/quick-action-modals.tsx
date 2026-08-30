import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { useToast } from "@/components/ui/toast";
import { api } from "@/lib/api-client";
import { Play, Pause } from "lucide-react";

// 1. QUICK TASK MODAL
export function QuickTaskModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [priority, setPriority] = useState("normal");
  const [category, setCategory] = useState("Pessoal");
  const [dueDate, setDueDate] = useState(new Date().toISOString().split("T")[0]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!title.trim()) {
      toast({ title: "Campo obrigatório", description: "Informe o título da tarefa", type: "warning" });
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/api/tasks/", {
        title,
        priority: priority === "normal" ? "media" : priority,
        category,
        due_date: dueDate,
        status: "pendente"
      });
      toast({ title: "Tarefa criada", description: "Tarefa adicionada com sucesso ao Resolva.", type: "success" });
      setTitle("");
      onClose();
    } catch (err: any) {
      toast({ title: "Erro ao criar tarefa", description: err.message || "Tente novamente.", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Nova Tarefa Rápida" size="md">
      <form onSubmit={handleCreate} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-surface-400 mb-1">O que precisa ser feito?</label>
          <Input 
            autoFocus
            placeholder="Ex: Comprar leite, Enviar relatório..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Prioridade</label>
            <select
              className="w-full h-10 px-3 rounded-lg bg-surface-900 border border-surface-700 text-white text-xs focus:outline-none focus:border-accent-500"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
            >
              <option value="baixa">Baixa</option>
              <option value="normal">Normal</option>
              <option value="alta">Alta</option>
              <option value="urgente">Urgente</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Categoria</label>
            <Input 
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Pessoal, Trabalho..."
              className="h-10 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Prazo</label>
            <Input 
              type="date"
              value={dueDate}
              onChange={(e) => setDueDate(e.target.value)}
              className="h-10 text-xs"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-2 border-t border-surface-800">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading} className="bg-accent-600 hover:bg-accent-500">
            {isLoading ? "Criando..." : "Criar Tarefa"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// 2. QUICK EXPENSE MODAL
export function QuickExpenseModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [description, setDescription] = useState("");
  const [amount, setAmount] = useState("");
  const [type, setType] = useState<"expense" | "income">("expense");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!description.trim() || !amount) {
      toast({ title: "Preencha os campos", description: "Descrição e valor são obrigatórios", type: "warning" });
      return;
    }

    setIsLoading(true);
    try {
      await api.post("/api/finances/transactions", {
        description,
        amount: parseFloat(amount),
        type,
        date
      });
      toast({ title: "Lançamento registrado", description: "Finanças atualizadas com sucesso.", type: "success" });
      setDescription("");
      setAmount("");
      onClose();
    } catch (err: any) {
      toast({ title: "Erro ao salvar", description: err.message || "Tente novamente.", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Novo Lançamento Financeiro" size="md">
      <form onSubmit={handleCreate} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-surface-400 mb-1">Descrição</label>
          <Input 
            autoFocus
            placeholder="Ex: Almoço executivo, Uber, Supermercado..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Tipo</label>
            <select
              className="w-full h-10 px-3 rounded-lg bg-surface-900 border border-surface-700 text-white text-xs focus:outline-none focus:border-accent-500"
              value={type}
              onChange={(e) => setType(e.target.value as any)}
            >
              <option value="expense">Despesa</option>
              <option value="income">Receita</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Valor (R$)</label>
            <Input 
              type="number"
              step="0.01"
              placeholder="0,00"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              className="h-10 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Data</label>
            <Input 
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="h-10 text-xs"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-2 pt-2 border-t border-surface-800">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading} className="bg-emerald-600 hover:bg-emerald-500">
            {isLoading ? "Salvando..." : "Adicionar Lançamento"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// 3. QUICK EVENT MODAL
export function QuickEventModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [title, setTitle] = useState("");
  const [date, setDate] = useState(new Date().toISOString().split("T")[0]);
  const [time, setTime] = useState("14:00");
  const [durationHours, setDurationHours] = useState("1");
  const [description, setDescription] = useState("");
  const [allDay, setAllDay] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleCreate = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!title.trim()) {
      toast({ title: "Campo obrigatório", description: "Informe o título do compromisso", type: "warning" });
      return;
    }

    setIsLoading(true);
    try {
      const startDateTime = new Date(`${date}T${time}:00`);
      const endDateTime = new Date(startDateTime.getTime() + (parseFloat(durationHours) || 1) * 3600000);

      await api.post("/api/calendar/events", {
        title,
        description,
        start_time: startDateTime.toISOString(),
        end_time: endDateTime.toISOString(),
        all_day: allDay,
        type: "appointment",
        source: "local"
      });

      toast({ title: "Compromisso agendado", description: "Evento registrado na agenda.", type: "success" });
      setTitle("");
      setDescription("");
      onClose();
    } catch (err: any) {
      toast({ title: "Erro ao agendar", description: err.message || "Tente novamente.", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Novo Compromisso" size="md">
      <form onSubmit={handleCreate} className="space-y-4">
        <div>
          <label className="block text-xs font-semibold text-surface-400 mb-1">Título</label>
          <Input 
            autoFocus
            placeholder="Ex: Reunião com equipe, Alinhamento de projeto..."
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div className="grid grid-cols-3 gap-3">
          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Data</label>
            <Input 
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              className="h-10 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Horário</label>
            <Input 
              type="time"
              value={time}
              onChange={(e) => setTime(e.target.value)}
              disabled={allDay}
              className="h-10 text-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-surface-400 mb-1">Duração (horas)</label>
            <Input 
              type="number"
              step="0.5"
              value={durationHours}
              onChange={(e) => setDurationHours(e.target.value)}
              disabled={allDay}
              className="h-10 text-xs"
            />
          </div>
        </div>

        <div className="flex items-center space-x-2 pt-1">
          <input 
            type="checkbox"
            id="allDayCheck"
            checked={allDay}
            onChange={(e) => setAllDay(e.target.checked)}
            className="rounded border-surface-700 bg-surface-900 text-accent-500"
          />
          <label htmlFor="allDayCheck" className="text-xs text-surface-300 cursor-pointer">
            Dia inteiro
          </label>
        </div>

        <div className="flex justify-end space-x-2 pt-2 border-t border-surface-800">
          <Button type="button" variant="ghost" onClick={onClose} disabled={isLoading}>
            Cancelar
          </Button>
          <Button type="submit" disabled={isLoading} className="bg-purple-600 hover:bg-purple-500">
            {isLoading ? "Salvando..." : "Salvar Evento"}
          </Button>
        </div>
      </form>
    </Modal>
  );
}

// 4. QUICK POMODORO MODAL
export function QuickPomodoroModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
  const [subjects, setSubjects] = useState<{ id: number; name: string }[]>([]);
  const [selectedSubjectId, setSelectedSubjectId] = useState<number | null>(null);
  const [durationMinutes] = useState(25);
  const [secondsRemaining, setSecondsRemaining] = useState(25 * 60);
  const [isRunning, setIsRunning] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    if (isOpen) {
      api.get<any[]>("/api/studies/subjects").then((data) => {
        if (data && data.length > 0) {
          setSubjects(data);
          setSelectedSubjectId(data[0].id);
        }
      }).catch(() => {});
    }
  }, [isOpen]);

  useEffect(() => {
    let interval: any = null;
    if (isRunning && secondsRemaining > 0) {
      interval = setInterval(() => {
        setSecondsRemaining((prev) => prev - 1);
      }, 1000);
    } else if (secondsRemaining === 0 && isRunning) {
      setIsRunning(false);
      handleFinishSession();
    }
    return () => clearInterval(interval);
  }, [isRunning, secondsRemaining]);

  const handleStart = () => {
    setIsRunning(true);
  };

  const handlePause = () => {
    setIsRunning(false);
  };

  const handleFinishSession = async () => {
    if (selectedSubjectId) {
      try {
        await api.post("/api/studies/sessions", {
          subject_id: selectedSubjectId,
          mode: "pomodoro",
          started_at: new Date(Date.now() - durationMinutes * 60000).toISOString(),
          ended_at: new Date().toISOString(),
          duration_minutes: durationMinutes,
          notes: "Sessão Pomodoro Rápida"
        });
        toast({ title: "Pomodoro Finalizado!", description: "Sua sessão de estudo foi salva com sucesso.", type: "success" });
      } catch (e) {}
    }
    onClose();
  };

  const formatTimer = (totalSeconds: number) => {
    const mins = Math.floor(totalSeconds / 60);
    const secs = totalSeconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Sessão Pomodoro Rápida" size="sm">
      <div className="flex flex-col items-center py-4 space-y-5">
        <div className="w-full">
          <label className="block text-xs font-semibold text-surface-400 mb-1">Matéria / Disciplina</label>
          <select
            className="w-full h-10 px-3 rounded-lg bg-surface-900 border border-surface-700 text-white text-xs focus:outline-none focus:border-accent-500"
            value={selectedSubjectId || ""}
            onChange={(e) => setSelectedSubjectId(Number(e.target.value))}
            disabled={isRunning}
          >
            {subjects.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
        </div>

        <div className="text-5xl font-mono font-bold tracking-widest text-accent-400 py-4">
          {formatTimer(secondsRemaining)}
        </div>

        <div className="flex items-center space-x-3">
          {!isRunning ? (
            <Button onClick={handleStart} className="bg-accent-600 hover:bg-accent-500 px-6">
              <Play className="h-4 w-4 mr-2" /> Iniciar
            </Button>
          ) : (
            <Button onClick={handlePause} variant="outline" className="px-6 border-surface-700">
              <Pause className="h-4 w-4 mr-2" /> Pausar
            </Button>
          )}

          <Button 
            variant="ghost" 
            onClick={() => {
              setIsRunning(false);
              setSecondsRemaining(durationMinutes * 60);
              onClose();
            }}
          >
            Cancelar
          </Button>
        </div>
      </div>
    </Modal>
  );
}

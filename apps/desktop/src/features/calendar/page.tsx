import { useState, useEffect, useMemo } from "react";
import { 
  Plus, Calendar as CalendarIcon, ChevronLeft, ChevronRight, 
  Clock, Trash2, Edit3, CheckCircle2, UserCheck, BookOpen
} from "lucide-react";
import { api } from "@/lib/api-client";
import { Modal } from "@/components/ui/modal";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { useToast } from "@/components/ui/toast";
import { ConfirmationDialog } from "@/components/shared/confirmation-dialog";
import { LoadingState } from "@/components/shared/loading-state";
import { formatTime, formatDate } from "@/lib/utils";

interface CalendarEvent {
  id: number;
  title: string;
  description: string | null;
  start_time: string;
  end_time: string | null;
  all_day: boolean;
  type: "event" | "appointment" | "study" | "task";
  recurrence: string | null;
  color: string | null;
  source: "local" | "google" | "outlook";
  created_at: string;
}

const DAYS_OF_WEEK = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"];
const MONTH_NAMES = [
  "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
  "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
];

export function CalendarPage() {
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [viewMode, setViewMode] = useState<"month" | "list">("month");

  // Modal states
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  // Form states
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [eventType, setEventType] = useState<"event" | "appointment" | "study" | "task">("event");
  const [startDate, setStartDate] = useState(new Date().toISOString().split("T")[0]);
  const [startTime, setStartTime] = useState("09:00");
  const [endTime, setEndTime] = useState("10:00");
  const [allDay, setAllDay] = useState(false);
  const [color, setColor] = useState("#8b5cf6");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const { toast } = useToast();

  const loadEvents = async () => {
    try {
      setIsLoading(true);
      const data = await api.get<CalendarEvent[]>("/api/calendar/");
      setEvents(data || []);
    } catch {
      toast({ title: "Erro ao carregar compromissos", type: "error" });
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadEvents();
  }, []);

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleToday = () => {
    const now = new Date();
    setCurrentDate(now);
    setSelectedDate(now);
  };

  const handleOpenCreate = (date?: Date) => {
    setEditingEvent(null);
    setTitle("");
    setDescription("");
    setEventType("event");
    const targetDate = date || selectedDate;
    setStartDate(targetDate.toISOString().split("T")[0]);
    setStartTime("09:00");
    setEndTime("10:00");
    setAllDay(false);
    setColor("#8b5cf6");
    setIsModalOpen(true);
  };

  const handleOpenEdit = (ev: CalendarEvent) => {
    setEditingEvent(ev);
    setTitle(ev.title);
    setDescription(ev.description || "");
    setEventType(ev.type);
    setStartDate(ev.start_time.split("T")[0]);
    setStartTime(ev.start_time.includes("T") ? ev.start_time.split("T")[1].slice(0, 5) : "09:00");
    setEndTime(ev.end_time && ev.end_time.includes("T") ? ev.end_time.split("T")[1].slice(0, 5) : "10:00");
    setAllDay(ev.all_day);
    setColor(ev.color || "#8b5cf6");
    setIsModalOpen(true);
  };

  const handleSaveEvent = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setIsSubmitting(true);
    const startIso = allDay ? `${startDate}T00:00:00` : `${startDate}T${startTime}:00`;
    const endIso = allDay ? `${startDate}T23:59:59` : `${startDate}T${endTime}:00`;

    const payload = {
      title: title.trim(),
      description: description.trim() || null,
      type: eventType,
      start_time: startIso,
      end_time: endIso,
      all_day: allDay,
      color,
    };

    try {
      if (editingEvent) {
        await api.put(`/api/calendar/${editingEvent.id}`, payload);
        toast({ title: "Compromisso atualizado", type: "success" });
      } else {
        await api.post("/api/calendar/", payload);
        toast({ title: "Compromisso agendado", type: "success" });
      }
      setIsModalOpen(false);
      loadEvents();
    } catch {
      toast({ title: "Erro ao salvar evento", type: "error" });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteId) return;
    try {
      await api.delete(`/api/calendar/${deleteId}`);
      toast({ title: "Evento excluído", type: "info" });
      setDeleteId(null);
      loadEvents();
    } catch {
      toast({ title: "Erro ao excluir evento", type: "error" });
    }
  };

  // Calendar Grid Days
  const calendarDays = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();

    const firstDayIndex = new Date(year, month, 1).getDay();
    const lastDate = new Date(year, month + 1, 0).getDate();
    const prevMonthLastDate = new Date(year, month, 0).getDate();

    const days: { date: Date; isCurrentMonth: boolean; isToday: boolean }[] = [];

    // Previous month padding days
    for (let i = firstDayIndex - 1; i >= 0; i--) {
      days.push({
        date: new Date(year, month - 1, prevMonthLastDate - i),
        isCurrentMonth: false,
        isToday: false,
      });
    }

    // Current month days
    const today = new Date();
    for (let i = 1; i <= lastDate; i++) {
      const d = new Date(year, month, i);
      const isToday =
        d.getDate() === today.getDate() &&
        d.getMonth() === today.getMonth() &&
        d.getFullYear() === today.getFullYear();

      days.push({
        date: d,
        isCurrentMonth: true,
        isToday,
      });
    }

    // Next month padding days to complete 35 or 42 grid cells
    const remaining = 35 - days.length > 0 ? 35 - days.length : 42 - days.length;
    for (let i = 1; i <= remaining; i++) {
      days.push({
        date: new Date(year, month + 1, i),
        isCurrentMonth: false,
        isToday: false,
      });
    }

    return days;
  }, [currentDate]);

  // Selected date events
  const selectedDateEvents = useMemo(() => {
    const targetStr = selectedDate.toISOString().split("T")[0];
    return events.filter((ev) => ev.start_time.startsWith(targetStr));
  }, [events, selectedDate]);

  const getEventIcon = (type: string) => {
    switch (type) {
      case "appointment": return UserCheck;
      case "study": return BookOpen;
      case "task": return CheckCircle2;
      default: return CalendarIcon;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border/40 pb-5">
        <div>
          <h1 className="text-2xl font-bold text-text-primary tracking-tight">Agenda</h1>
          <p className="text-sm text-text-secondary">
            Gerencie reuniões, sessões de estudo e compromissos do seu calendário.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => handleOpenCreate()} className="gap-2 shrink-0">
            <Plus className="w-4 h-4" />
            Novo Evento
          </Button>
        </div>
      </div>

      {/* Calendar Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 glass-card p-4">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-bold text-text-primary min-w-[180px]">
            {MONTH_NAMES[currentDate.getMonth()]} {currentDate.getFullYear()}
          </h2>
          <div className="flex items-center gap-1 bg-surface-elevated/60 rounded-lg p-1 border border-border/60">
            <button
              onClick={handlePrevMonth}
              className="p-1 rounded text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <button
              onClick={handleToday}
              className="px-2.5 py-0.5 text-xs font-semibold text-text-secondary hover:text-text-primary hover:bg-surface-hover rounded transition-colors cursor-pointer"
            >
              Hoje
            </button>
            <button
              onClick={handleNextMonth}
              className="p-1 rounded text-text-secondary hover:text-text-primary hover:bg-surface-hover transition-colors cursor-pointer"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <div className="inline-flex rounded-lg bg-surface-elevated/60 p-1 border border-border/60">
            <button
              onClick={() => setViewMode("month")}
              className={`px-3 py-1 rounded text-xs font-semibold transition-colors cursor-pointer ${
                viewMode === "month" ? "bg-accent text-text-primary" : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Mês
            </button>
            <button
              onClick={() => setViewMode("list")}
              className={`px-3 py-1 rounded text-xs font-semibold transition-colors cursor-pointer ${
                viewMode === "list" ? "bg-accent text-text-primary" : "text-text-secondary hover:text-text-primary"
              }`}
            >
              Lista Completa
            </button>
          </div>
        </div>
      </div>

      {isLoading ? (
        <LoadingState message="Carregando eventos da agenda..." />
      ) : viewMode === "month" ? (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Month Calendar Grid (2 Cols) */}
          <div className="lg:col-span-2 glass-card p-5">
            {/* Days header */}
            <div className="grid grid-cols-7 gap-1 text-center mb-2">
              {DAYS_OF_WEEK.map((day) => (
                <div key={day} className="text-xs font-bold text-text-secondary py-1 uppercase">
                  {day}
                </div>
              ))}
            </div>

            {/* Grid Cells */}
            <div className="grid grid-cols-7 gap-1">
              {calendarDays.map((cell, idx) => {
                const dateStr = cell.date.toISOString().split("T")[0];
                const dayEvents = events.filter((e) => e.start_time.startsWith(dateStr));
                const isSelected =
                  cell.date.getDate() === selectedDate.getDate() &&
                  cell.date.getMonth() === selectedDate.getMonth() &&
                  cell.date.getFullYear() === selectedDate.getFullYear();

                return (
                  <div
                    key={idx}
                    onClick={() => {
                      setSelectedDate(cell.date);
                    }}
                    onDoubleClick={() => handleOpenCreate(cell.date)}
                    className={`min-h-[80px] p-1.5 rounded-lg border transition-all cursor-pointer flex flex-col justify-between ${
                      isSelected
                        ? "border-accent bg-accent/10 shadow-sm"
                        : cell.isCurrentMonth
                        ? "border-border/80 bg-surface/40 hover:border-border hover:bg-surface-elevated/40"
                        : "border-surface-900/40 bg-background/30 opacity-30"
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={`text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center ${
                          cell.isToday
                            ? "bg-accent text-text-primary"
                            : isSelected
                            ? "text-accent-light font-extrabold"
                            : "text-text-secondary"
                        }`}
                      >
                        {cell.date.getDate()}
                      </span>
                      {dayEvents.length > 0 && (
                        <span className="text-[10px] text-text-secondary font-medium px-1 rounded bg-surface-elevated">
                          {dayEvents.length}
                        </span>
                      )}
                    </div>

                    {/* Mini event tags */}
                    <div className="space-y-0.5 mt-1 overflow-hidden">
                      {dayEvents.slice(0, 2).map((ev) => (
                        <div
                          key={ev.id}
                          className="text-[10px] truncate px-1 py-0.5 rounded text-text-primary font-medium"
                          style={{ backgroundColor: ev.color || "#8b5cf6" }}
                          title={ev.title}
                        >
                          {ev.title}
                        </div>
                      ))}
                      {dayEvents.length > 2 && (
                        <span className="text-[9px] text-text-muted block text-right">
                          +{dayEvents.length - 2} mais
                        </span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Selected Day Agenda Sidebar (1 Col) */}
          <div className="glass-card p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div>
                <h3 className="text-sm font-bold text-text-primary">
                  {formatDate(selectedDate)}
                </h3>
                <span className="text-xs text-text-secondary">
                  {selectedDateEvents.length} compromisso(s)
                </span>
              </div>
              <Button
                size="sm"
                variant="secondary"
                onClick={() => handleOpenCreate(selectedDate)}
                className="gap-1 border border-border"
              >
                <Plus className="w-3.5 h-3.5" />
                Novo
              </Button>
            </div>

            {selectedDateEvents.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 text-center text-text-muted">
                <CalendarIcon className="w-8 h-8 mb-2 opacity-30" />
                <p className="text-xs">Nenhum compromisso marcado para este dia.</p>
              </div>
            ) : (
              <div className="space-y-2.5 max-h-[460px] overflow-y-auto pr-1">
                {selectedDateEvents.map((ev) => {
                  const Icon = getEventIcon(ev.type);
                  return (
                    <div
                      key={ev.id}
                      className="p-3 rounded-lg border border-border/60 bg-surface/60 hover:border-border-strong transition-colors space-y-2"
                    >
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex items-center gap-2">
                          <div
                            className="p-1.5 rounded-md text-text-primary"
                            style={{ backgroundColor: ev.color || "#8b5cf6" }}
                          >
                            <Icon className="w-3.5 h-3.5" />
                          </div>
                          <div>
                            <h4 className="text-xs font-bold text-text-primary">{ev.title}</h4>
                            <div className="flex items-center gap-2 text-[10px] text-text-secondary mt-0.5">
                              <Clock className="w-3 h-3 text-text-muted" />
                              <span>{ev.all_day ? "Dia Inteiro" : `${formatTime(ev.start_time)} - ${formatTime(ev.end_time || ev.start_time)}`}</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex items-center gap-1">
                          <button
                            onClick={() => handleOpenEdit(ev)}
                            className="p-1 text-text-secondary hover:text-text-primary rounded transition-colors cursor-pointer"
                          >
                            <Edit3 className="w-3 h-3" />
                          </button>
                          <button
                            onClick={() => setDeleteId(ev.id)}
                            className="p-1 text-text-secondary hover:text-error rounded transition-colors cursor-pointer"
                          >
                            <Trash2 className="w-3 h-3" />
                          </button>
                        </div>
                      </div>

                      {ev.description && (
                        <p className="text-xs text-text-secondary leading-relaxed bg-background/40 p-2 rounded border border-border/40">
                          {ev.description}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      ) : (
        /* List View */
        <div className="glass-card p-5 space-y-3">
          {events.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-16 text-center text-text-muted">
              <CalendarIcon className="w-8 h-8 mb-2 opacity-30" />
              <p className="text-xs">Nenhum evento registrado no calendário.</p>
            </div>
          ) : (
            <div className="space-y-2">
              {events.map((ev) => {
                const Icon = getEventIcon(ev.type);
                return (
                  <div
                    key={ev.id}
                    className="glass-card p-3.5 flex items-center justify-between gap-4 hover:border-border-strong transition-colors"
                  >
                    <div className="flex items-center gap-3.5">
                      <div
                        className="p-2 rounded-lg text-text-primary shrink-0"
                        style={{ backgroundColor: ev.color || "#8b5cf6" }}
                      >
                        <Icon className="w-4 h-4" />
                      </div>
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-semibold text-text-primary">{ev.title}</span>
                          <Badge variant="outline" className="text-[10px] py-0 px-1.5 capitalize border-border">
                            {ev.type}
                          </Badge>
                        </div>
                        <div className="flex items-center gap-3 text-xs text-text-secondary mt-0.5">
                          <span className="flex items-center gap-1">
                            <CalendarIcon className="w-3.5 h-3.5 text-text-muted" />
                            {formatDate(ev.start_time)}
                          </span>
                          <span className="flex items-center gap-1">
                            <Clock className="w-3.5 h-3.5 text-text-muted" />
                            {ev.all_day ? "Dia Inteiro" : `${formatTime(ev.start_time)} - ${formatTime(ev.end_time || ev.start_time)}`}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleOpenEdit(ev)}
                        className="p-1.5 text-text-secondary hover:text-text-primary rounded hover:bg-surface-elevated transition-colors cursor-pointer"
                      >
                        <Edit3 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => setDeleteId(ev.id)}
                        className="p-1.5 text-text-secondary hover:text-error rounded hover:bg-surface-elevated transition-colors cursor-pointer"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Create / Edit Event Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={editingEvent ? "Editar Compromisso" : "Novo Compromisso na Agenda"}
        size="md"
      >
        <form onSubmit={handleSaveEvent} className="space-y-4">
          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Título do Evento *</label>
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Ex: Reunião com Equipe, Prova de IA..."
              required
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Descrição ou Pauta</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={2}
              placeholder="Notas, links de reunião ou tópicos a tratar..."
              className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary placeholder-surface-500 focus:outline-none focus:ring-2 focus:ring-accent-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Tipo de Evento</label>
              <select
                value={eventType}
                onChange={(e) => setEventType(e.target.value as any)}
                className="w-full rounded-md border border-border bg-surface-elevated px-3 py-2 text-sm text-text-primary focus:outline-none focus:ring-2 focus:ring-accent-500"
              >
                <option value="event">Evento Geral</option>
                <option value="appointment">Reunião / Compromisso</option>
                <option value="study">Sessão de Estudo</option>
                <option value="task">Prazo de Tarefa</option>
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

          <div>
            <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Data</label>
            <Input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
          </div>

          <div className="flex items-center gap-2 py-1">
            <input
              type="checkbox"
              id="allDayCheck"
              checked={allDay}
              onChange={(e) => setAllDay(e.target.checked)}
              className="rounded border-border bg-surface-elevated text-accent focus:ring-accent-500"
            />
            <label htmlFor="allDayCheck" className="text-xs text-text-secondary cursor-pointer">
              Compromisso de dia inteiro
            </label>
          </div>

          {!allDay && (
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Início</label>
                <Input
                  type="time"
                  value={startTime}
                  onChange={(e) => setStartTime(e.target.value)}
                />
              </div>

              <div>
                <label className="text-xs font-semibold text-text-secondary mb-1.5 block">Término</label>
                <Input
                  type="time"
                  value={endTime}
                  onChange={(e) => setEndTime(e.target.value)}
                />
              </div>
            </div>
          )}

          <div className="flex justify-end gap-3 pt-3 border-t border-border">
            <Button variant="ghost" type="button" onClick={() => setIsModalOpen(false)}>
              Cancelar
            </Button>
            <Button type="submit" isLoading={isSubmitting}>
              Salvar Evento
            </Button>
          </div>
        </form>
      </Modal>

      {/* Delete Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={deleteId !== null}
        onClose={() => setDeleteId(null)}
        onConfirm={handleDelete}
        title="Excluir Evento"
        message="Tem certeza que deseja excluir este compromisso da sua agenda?"
        confirmLabel="Excluir"
        variant="destructive"
      />
    </div>
  );
}

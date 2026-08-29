// Task types matching backend schema

export type Priority = "baixa" | "media" | "alta" | "urgente";
export type TaskStatus = "pendente" | "em_andamento" | "concluida" | "arquivada";
export type Recurrence = "none" | "daily" | "weekly" | "monthly";

export interface Task {
  id: number;
  title: string;
  description: string | null;
  priority: Priority;
  status: TaskStatus;
  category: string | null;
  due_date: string | null;
  due_time: string | null;
  recurrence: Recurrence;
  tags: string[];
  parent_task_id: number | null;
  completed_at: string | null;
  created_at: string;
  updated_at: string;
  subtasks: Subtask[];
}

export interface Subtask {
  id: number;
  task_id: number;
  title: string;
  completed: boolean;
  sort_order: number;
  created_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  priority?: Priority;
  status?: TaskStatus;
  category?: string;
  due_date?: string;
  due_time?: string;
  recurrence?: Recurrence;
  tags?: string[];
  parent_task_id?: number;
  subtasks?: { title: string }[];
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  priority?: Priority;
  status?: TaskStatus;
  category?: string;
  due_date?: string;
  due_time?: string;
  recurrence?: Recurrence;
  tags?: string[];
}

export interface TaskSummary {
  total: number;
  pending: number;
  in_progress: number;
  completed: number;
  overdue: number;
}

export type TaskFilter = "all" | "today" | "overdue" | "high_priority" | "completed";

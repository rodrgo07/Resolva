// Study types

export interface StudySubject {
  id: number;
  name: string;
  description: string | null;
  priority: string;
  progress: number;
  weekly_goal_hours: number;
  monthly_goal_hours: number;
  color: string;
  created_at: string;
  updated_at: string;
}

export interface SubjectCreate {
  name: string;
  description?: string;
  priority?: string;
  weekly_goal_hours?: number;
  monthly_goal_hours?: number;
  color?: string;
}

export interface SubjectUpdate {
  name?: string;
  description?: string;
  priority?: string;
  progress?: number;
  weekly_goal_hours?: number;
  monthly_goal_hours?: number;
  color?: string;
}

export type StudyMode = "pomodoro" | "free";

export interface StudySession {
  id: number;
  subject_id: number;
  subject_name: string;
  mode: StudyMode;
  started_at: string;
  ended_at: string | null;
  duration_minutes: number;
  notes: string | null;
  created_at: string;
}

export interface SessionCreate {
  subject_id: number;
  mode: StudyMode;
  started_at: string;
  ended_at?: string;
  duration_minutes: number;
  notes?: string;
}

export interface StudySummary {
  today_minutes: number;
  week_minutes: number;
  month_minutes: number;
  daily_goal_minutes: number;
  weekly_goal_minutes: number;
  streak_days: number;
}

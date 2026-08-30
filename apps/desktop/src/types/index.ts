// Notification types
export type NotificationType = 
  | "INFO" | "REMINDER" | "TASK_OVERDUE" | "EMAIL_IMPORTANT" | "EMAIL_URGENT" 
  | "CALENDAR_UPCOMING" | "STUDY_REMINDER" | "FINANCE_ALERT" | "SYNC_STATUS" 
  | "AUTOMATION_RESULT" | "SYSTEM" | "AGENT_RECOMMENDATION"
  | "task" | "study" | "finance" | "email" | "automation" | "system" | "ai";

export type NotificationPriority = "LOW" | "NORMAL" | "IMPORTANT" | "URGENT" | "CRITICAL" | "low" | "normal" | "high";

export interface Notification {
  id: number;
  type: NotificationType;
  title: string;
  message: string;
  priority: NotificationPriority;
  source?: string;
  source_id?: string | null;
  is_read: boolean;
  read_at?: string | null;
  dismissed_at?: string | null;
  scheduled_for?: string | null;
  expires_at?: string | null;
  action_type?: string | null;
  action_payload?: Record<string, unknown> | null;
  action_data?: Record<string, unknown> | null;
  requires_confirmation?: boolean;
  status?: string;
  created_at: string;
}

export interface NotificationSummary {
  unread_count: number;
  total_count: number;
  urgent_count: number;
  important_count: number;
  by_source: Record<string, number>;
}

// Activity types
export interface ActivityLog {
  id: number;
  type: string;
  action: string;
  description: string;
  metadata: Record<string, unknown> | null;
  created_at: string;
}

// AI types
export interface AIMessage {
  id: number;
  conversation_id: number;
  role: "user" | "assistant" | "system" | "tool";
  content: string;
  tool_calls: unknown[] | null;
  tool_results: unknown[] | null;
  created_at: string;
}

export interface AIConversation {
  id: number;
  title: string;
  created_at: string;
  updated_at: string;
  messages: AIMessage[];
}

export interface ChatRequest {
  message: string;
  conversation_id?: number;
}

export interface ChatResponse {
  message: string;
  conversation_id: number;
  tool_calls_made: string[];
}

// Calendar types
export interface CalendarEvent {
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
  updated_at: string;
}

export interface EventCreate {
  title: string;
  description?: string;
  start_time: string;
  end_time?: string;
  all_day?: boolean;
  type?: string;
  recurrence?: string;
  color?: string;
}

// Settings types
export interface AppSettings {
  language: string;
  auto_start: boolean;
  minimize_to_tray: boolean;
  notifications_enabled: boolean;
  theme: "dark" | "light";
  accent_color: string;
  density: "compact" | "normal" | "comfortable";
  animations_enabled: boolean;
  ai_provider: string;
  ai_model: string;
  ai_temperature: number;
}

// Search types
export interface SearchResult {
  type: "task" | "expense" | "subject" | "event" | "conversation" | "setting";
  id: number;
  title: string;
  subtitle: string;
  icon: string;
}

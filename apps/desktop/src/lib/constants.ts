export const API_BASE_URL = "http://127.0.0.1:8700";

export const APP_NAME = "Resolva";
export const APP_VERSION = "0.1.0";
export const APP_DESCRIPTION = "Seu centro de comando pessoal.";

export const PRIORITIES = {
  baixa: { label: "Baixa", color: "text-success", bg: "bg-green-400/10", border: "border-green-400/20" },
  media: { label: "Média", color: "text-warning", bg: "bg-yellow-400/10", border: "border-yellow-400/20" },
  alta: { label: "Alta", color: "text-orange-400", bg: "bg-orange-400/10", border: "border-orange-400/20" },
  urgente: { label: "Urgente", color: "text-error", bg: "bg-red-400/10", border: "border-red-400/20" },
} as const;

export const TASK_STATUSES = {
  pendente: { label: "Pendente", color: "text-text-secondary" },
  em_andamento: { label: "Em andamento", color: "text-accent-light" },
  concluida: { label: "Concluída", color: "text-success" },
  arquivada: { label: "Arquivada", color: "text-text-muted" },
} as const;

export const EXPENSE_CATEGORIES = [
  { value: "alimentacao", label: "Alimentação", icon: "🍔" },
  { value: "transporte", label: "Transporte", icon: "🚗" },
  { value: "faculdade", label: "Faculdade", icon: "🎓" },
  { value: "moradia", label: "Moradia", icon: "🏠" },
  { value: "lazer", label: "Lazer", icon: "🎮" },
  { value: "compras", label: "Compras", icon: "🛒" },
  { value: "assinaturas", label: "Assinaturas", icon: "📱" },
  { value: "saude", label: "Saúde", icon: "💊" },
  { value: "outros", label: "Outros", icon: "📦" },
] as const;

export const INCOME_CATEGORIES = [
  { value: "salario", label: "Salário", icon: "💰" },
  { value: "renda_extra", label: "Renda Extra", icon: "💵" },
  { value: "outros", label: "Outros", icon: "📦" },
] as const;

export const KEYBOARD_SHORTCUTS = {
  search: "Ctrl+K",
  newTask: "Ctrl+N",
  openAI: "Ctrl+Shift+A",
  closeModal: "Escape",
} as const;

from typing import Dict, Any, List, Optional
from enum import Enum

class ActionRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"

class ActionPermissionLevel(str, Enum):
    READ = "READ"
    WRITE_LOW = "WRITE_LOW"
    WRITE_MEDIUM = "WRITE_MEDIUM"
    WRITE_HIGH = "WRITE_HIGH"

HOMOLOGATED_ACTION_CATALOG: Dict[str, Dict[str, Any]] = {
    # 1. READ ACTIONS
    "GET_TODAY_CONTEXT": {
        "description": "Obtém resumo do dia (tarefas, eventos, hábitos e pendências)",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": ["include_weather", "include_finance"],
        "category": "CONTEXT"
    },
    "GET_TASKS": {
        "description": "Lista tarefas com filtros seguros de status ou prioridade",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": ["status", "priority", "limit"],
        "category": "TASK"
    },
    "GET_OVERDUE_TASKS": {
        "description": "Lista tarefas atrasadas até o momento atual",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": ["limit"],
        "category": "TASK"
    },
    "GET_NEXT_TASK": {
        "description": "Obtém a próxima tarefa recomendada da fila",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": ["category", "priority"],
        "category": "TASK"
    },
    "GET_UPCOMING_EVENTS": {
        "description": "Lista próximos compromissos da agenda",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": ["minutes_ahead", "limit"],
        "category": "CALENDAR"
    },
    "GET_NOTIFICATION_SUMMARY": {
        "description": "Obtém contagem e resumo de notificações não lidas",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": [],
        "category": "NOTIFICATION"
    },
    "GET_FINANCE_SUMMARY": {
        "description": "Obtém resumo financeiro consolidado do mês",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": ["month", "year"],
        "category": "FINANCE"
    },
    "GET_SYNC_STATUS": {
        "description": "Verifica estado de sincronização e fila offline",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": [],
        "category": "SYSTEM"
    },
    "GET_DESKTOP_STATUS": {
        "description": "Obtém status do Desktop, banco SQLite e processos",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.READ,
        "confirmation_required": False,
        "allowed_parameters": [],
        "category": "SYSTEM"
    },

    # 2. WRITE LOW RISK ACTIONS
    "CREATE_TASK": {
        "description": "Cria uma nova tarefa no Resolva",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["title", "description", "priority", "due_date", "category_id"],
        "category": "TASK"
    },
    "COMPLETE_TASK": {
        "description": "Marca uma tarefa existente como concluída",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["task_id", "title_match"],
        "category": "TASK"
    },
    "CREATE_CALENDAR_EVENT": {
        "description": "Agenda um evento no calendário",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["title", "start_time", "end_time", "description", "color"],
        "category": "CALENDAR"
    },
    "CREATE_EXPENSE": {
        "description": "Registra uma despesa financeira",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["description", "amount", "category_id", "date"],
        "category": "FINANCE"
    },
    "CREATE_STUDY_SESSION": {
        "description": "Registra uma sessão de estudos concluída ou planejada",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["subject_id", "duration_minutes", "mode", "notes"],
        "category": "STUDY"
    },
    "START_POMODORO": {
        "description": "Inicia um timer de Pomodoro sincronizado com Live State",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["duration_seconds", "task_id", "block_name"],
        "category": "FOCUS"
    },
    "STOP_POMODORO": {
        "description": "Interrompe ou pausa a sessão de foco atual",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": [],
        "category": "FOCUS"
    },
    "UPDATE_LIVE_STATE": {
        "description": "Atualiza o estado global de atividade no ecossistema",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["type", "status", "metadata"],
        "category": "LIVE_STATE"
    },
    "SHOW_NOTIFICATION": {
        "description": "Envia uma notificação segura para o Desktop e Mobile",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["title", "message", "type", "priority"],
        "category": "NOTIFICATION"
    },
    "MARK_NOTIFICATION_READ": {
        "description": "Marca notificações como lidas",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["notification_id", "all"],
        "category": "NOTIFICATION"
    },
    "SYNC_NOW": {
        "description": "Dispara reconciliação imediata da fila de sincronização",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": [],
        "category": "SYNC"
    },
    "CREATE_BACKUP": {
        "description": "Gera um backup instantâneo da base SQLite do Resolva",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["comment"],
        "category": "SYSTEM"
    },
    "PREPARE_DAILY_PLAN": {
        "description": "Aciona o Planning Engine para estruturar o plano diário",
        "risk_level": ActionRiskLevel.LOW,
        "permission_level": ActionPermissionLevel.WRITE_LOW,
        "confirmation_required": False,
        "allowed_parameters": ["user_name", "focus_theme"],
        "category": "AGENT"
    },

    # 3. WRITE MEDIUM / HIGH RISK (REQUIRE CONFIRMATION)
    "EXECUTE_APPROVED_AUTOMATION": {
        "description": "Executa uma sub-automação pré-aprovada",
        "risk_level": ActionRiskLevel.MEDIUM,
        "permission_level": ActionPermissionLevel.WRITE_MEDIUM,
        "confirmation_required": True,
        "allowed_parameters": ["automation_id", "parameters"],
        "category": "AUTOMATION"
    },
    "DELETE_TASK": {
        "description": "Remove uma tarefa do banco de dados",
        "risk_level": ActionRiskLevel.HIGH,
        "permission_level": ActionPermissionLevel.WRITE_HIGH,
        "confirmation_required": True,
        "allowed_parameters": ["task_id"],
        "category": "TASK"
    },
    "DELETE_EVENT": {
        "description": "Remove um evento do calendário",
        "risk_level": ActionRiskLevel.HIGH,
        "permission_level": ActionPermissionLevel.WRITE_HIGH,
        "confirmation_required": True,
        "allowed_parameters": ["event_id"],
        "category": "CALENDAR"
    },
    "DELETE_EXPENSE": {
        "description": "Exclui um registro financeiro",
        "risk_level": ActionRiskLevel.HIGH,
        "permission_level": ActionPermissionLevel.WRITE_HIGH,
        "confirmation_required": True,
        "allowed_parameters": ["expense_id"],
        "category": "FINANCE"
    }
}

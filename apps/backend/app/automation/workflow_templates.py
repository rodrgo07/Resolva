from typing import List, Dict, Any

WORKFLOW_TEMPLATES: List[Dict[str, Any]] = [
    {
        "template_id": "tpl_morning_planning",
        "name": "Planejamento Matinal",
        "description": "Obtém contexto do dia, prepara plano com o Agent e notifica no Desktop e Mobile.",
        "category": "ROUTINE",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "TIME",
            "time": "07:00",
            "days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        },
        "condition_config": {
            "field": "desktop_status.desktop_online",
            "operator": "EQ",
            "value": True
        },
        "steps": [
            {
                "name": "Obter Contexto do Dia",
                "action_type": "GET_TODAY_CONTEXT",
                "parameters": {"include_weather": False, "include_finance": True}
            },
            {
                "name": "Preparar Plano Diário",
                "action_type": "PREPARE_DAILY_PLAN",
                "parameters": {"user_name": "Rodrigo"}
            },
            {
                "name": "Notificar Planejamento Concluído",
                "action_type": "SHOW_NOTIFICATION",
                "parameters": {
                    "title": "Planejamento Matinal Pronto",
                    "message": "Seu plano para hoje foi estruturado pelo Resolva Agent.",
                    "type": "info",
                    "priority": "HIGH"
                }
            }
        ]
    },
    {
        "template_id": "tpl_study_start",
        "name": "Início do Estudo",
        "description": "Inicia timer Pomodoro de 25min e notifica quando o horário de estudo chegar.",
        "category": "STUDY",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "TIME",
            "time": "19:00",
            "days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
        },
        "condition_config": {
            "field": "live_session.status",
            "operator": "NEQ",
            "value": "RUNNING"
        },
        "steps": [
            {
                "name": "Iniciar Pomodoro de Estudo",
                "action_type": "START_POMODORO",
                "parameters": {"duration_seconds": 1500, "block_name": "Sessão Noturna de Estudo"}
            },
            {
                "name": "Notificar Início de Foco",
                "action_type": "SHOW_NOTIFICATION",
                "parameters": {
                    "title": "Hora de Estudar",
                    "message": "Bloco de foco iniciado. Modo Não Perturbe ativo.",
                    "type": "info"
                }
            }
        ]
    },
    {
        "template_id": "tpl_pomodoro_end",
        "name": "Finalização do Pomodoro",
        "description": "Registra a sessão de estudos ao concluir o Pomodoro e busca a próxima tarefa.",
        "category": "FOCUS",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "EVENT",
            "event": "POMODORO_COMPLETED"
        },
        "condition_config": None,
        "steps": [
            {
                "name": "Registrar Sessão de Estudo",
                "action_type": "CREATE_STUDY_SESSION",
                "parameters": {"duration_minutes": 25, "mode": "POMODORO", "notes": "Concluído via Workflow"}
            },
            {
                "name": "Buscar Próxima Tarefa",
                "action_type": "GET_NEXT_TASK",
                "parameters": {"limit": 1}
            },
            {
                "name": "Notificar Próximo Passo",
                "action_type": "SHOW_NOTIFICATION",
                "parameters": {
                    "title": "Pomodoro Finalizado",
                    "message": "Excelente! Faça uma pausa de 5 minutos antes da próxima tarefa.",
                    "type": "success"
                }
            }
        ]
    },
    {
        "template_id": "tpl_overdue_task_alert",
        "name": "Alerta de Tarefas Atrasadas",
        "description": "Alerta sobre pendências urgentes e recomenda replanejamento.",
        "category": "TASK",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "EVENT",
            "event": "TASK_OVERDUE"
        },
        "condition_config": None,
        "steps": [
            {
                "name": "Listar Tarefas Atrasadas",
                "action_type": "GET_OVERDUE_TASKS",
                "parameters": {"limit": 5}
            },
            {
                "name": "Notificar Tarefas Atrasadas",
                "action_type": "SHOW_NOTIFICATION",
                "parameters": {
                    "title": "Atenção: Tarefas Atrasadas",
                    "message": "Existem pendências com prazo vencido que precisam de atenção.",
                    "type": "warning",
                    "priority": "HIGH"
                }
            }
        ]
    },
    {
        "template_id": "tpl_auto_backup",
        "name": "Backup Automático Diário",
        "description": "Gera backup do banco SQLite com segurança.",
        "category": "SYSTEM",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "SCHEDULE",
            "time": "23:00",
            "days": ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        },
        "condition_config": None,
        "steps": [
            {
                "name": "Criar Backup do Banco",
                "action_type": "CREATE_BACKUP",
                "parameters": {"comment": "Backup automático noturno via Workflow"}
            },
            {
                "name": "Notificar Backup Concluído",
                "action_type": "SHOW_NOTIFICATION",
                "parameters": {
                    "title": "Backup Realizado",
                    "message": "Base de dados protegida com sucesso.",
                    "type": "info"
                }
            }
        ]
    },
    {
        "template_id": "tpl_focus_routine",
        "name": "Rotina de Modo Foco",
        "description": "Sincroniza fila offline, inicia pomodoro e atualiza live state.",
        "category": "FOCUS",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "EVENT",
            "event": "FOCUS_BLOCK_STARTED"
        },
        "condition_config": None,
        "steps": [
            {
                "name": "Sincronizar Dados",
                "action_type": "SYNC_NOW",
                "parameters": {}
            },
            {
                "name": "Iniciar Pomodoro",
                "action_type": "START_POMODORO",
                "parameters": {"duration_seconds": 1500}
            },
            {
                "name": "Atualizar Live State",
                "action_type": "UPDATE_LIVE_STATE",
                "parameters": {"type": "POMODORO", "status": "RUNNING"}
            }
        ]
    },
    {
        "template_id": "tpl_meeting_prep",
        "name": "Preparação para Reunião",
        "description": "Avisa sobre reuniões nos próximos 15 minutos e resume tarefas relacionadas.",
        "category": "CALENDAR",
        "safety_level": "AUTO_LOW_RISK",
        "trigger_config": {
            "type": "EVENT",
            "event": "CALENDAR_EVENT_UPCOMING"
        },
        "condition_config": None,
        "steps": [
            {
                "name": "Buscar Próximos Compromissos",
                "action_type": "GET_UPCOMING_EVENTS",
                "parameters": {"minutes_ahead": 15, "limit": 3}
            },
            {
                "name": "Notificar Reunião Próxima",
                "action_type": "SHOW_NOTIFICATION",
                "parameters": {
                    "title": "Compromisso em 15 Minutos",
                    "message": "Verifique suas anotações e link de chamada antes de iniciar.",
                    "type": "info"
                }
            }
        ]
    }
]

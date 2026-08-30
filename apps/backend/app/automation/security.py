import re
from typing import Tuple, Dict, Any

# Whitelist estrita de ações suportadas pelo Resolva Automation Engine
ALLOWED_ACTIONS = [
    # Notificações e Mensagens do Agent
    "CREATE_NOTIFICATION",
    "SHOW_NOTIFICATION",
    "SHOW_AGENT_MESSAGE",
    "send_notification",
    
    # Tarefas & Calendário
    "CREATE_TASK",
    "COMPLETE_TASK",
    "CREATE_CALENDAR_EVENT",
    "create_task",
    "update_task",
    "complete_task",
    
    # Estudos & Pomodoro
    "START_STUDY_SESSION",
    
    # Finanças
    "CREATE_EXPENSE",
    "create_expense",
    
    # E-mails & Sincronização & Backup
    "SYNC_EMAIL",
    "SYNC_NOW",
    "CREATE_BACKUP",
    
    # Resumos
    "GENERATE_DAILY_SUMMARY",
    "GENERATE_WEEKLY_SUMMARY",
    
    # Interface & Navegação Nativa
    "OPEN_RESOLVA",
    "OPEN_COMMAND_PALETTE",
    
    # Execução Segura de Aplicativos Windows (Apenas Whitelist)
    "OPEN_APPLICATION",
    "open_application"
]

# Whitelist de aplicativos Windows autorizados
ALLOWED_WINDOWS_APPS = [
    "vscode", "code", "code.exe",
    "chrome", "chrome.exe",
    "brave", "brave.exe",
    "edge", "msedge.exe",
    "firefox", "firefox.exe",
    "spotify", "spotify.exe",
    "discord", "discord.exe",
    "notepad", "notepad.exe",
    "calc", "calculator", "calc.exe"
]

DANGEROUS_PATTERNS = [
    r"rm\s+-rf",
    r"drop\s+table",
    r"delete\s+from",
    r"format\s+[a-z]:",
    r"powershell",
    r"cmd\.exe",
    r"exec\(",
    r"eval\(",
    r"curl\s+",
    r"wget\s+",
    r"invoke-expression",
    r"downloadstring"
]

def validate_action_type(act_type: str) -> bool:
    return act_type in ALLOWED_ACTIONS

def check_action_safety(action: Dict[str, Any]) -> Tuple[bool, str]:
    action_type = action.get("type", "")
    
    if not validate_action_type(action_type):
        return False, f"Tipo de ação '{action_type}' não permitida na whitelist do Resolva."
        
    config = action.get("config", {})
    config_str = str(config).lower()

    # Bloqueio de padrões perigosos de shell / SQL / script
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, config_str):
            return False, f"Padrão potencialmente perigoso detectado nos parâmetros da ação: {pattern}"

    # Validação de Aplicativos Windows
    if action_type.upper() in ["OPEN_APPLICATION", "OPEN_APP"]:
        app_name = str(config.get("app_name", "")).lower().strip()
        if app_name not in ALLOWED_WINDOWS_APPS:
            return False, f"Aplicativo '{app_name}' não consta na whitelist de aplicativos permitidos do Windows ({', '.join(ALLOWED_WINDOWS_APPS[:6])})."

    return True, "Ação validada e segura para execução."

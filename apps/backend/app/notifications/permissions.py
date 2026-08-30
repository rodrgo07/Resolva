from typing import Dict, Any, Tuple
from app.core.exceptions import PermissionError
from app.core.logging import logger

class NotificationPermissionService:
    """
    Controla permissões de execução de ações seguras originadas em notificações.
    Zero Shell, Zero SQL arbitrário, confirmação obrigatória para ações MEDIUM/HIGH.
    """
    SAFE_ACTIONS = {
        "OPEN_TASK": "READ",
        "OPEN_CALENDAR": "READ",
        "OPEN_EMAIL": "READ",
        "OPEN_STUDIES": "READ",
        "OPEN_FINANCES": "READ",
        "OPEN_MODULE": "READ",
        "NAVIGATE": "READ",
        "COMPLETE_TASK": "WRITE",
        "POSTPONE_TASK": "WRITE",
        "START_POMODORO": "WRITE",
        "SYNC_NOW": "WRITE",
        "CREATE_BACKUP": "WRITE"
    }

    @classmethod
    def validate_action(cls, action_type: str, action_payload: Dict[str, Any], is_confirmed: bool = False) -> Tuple[bool, str]:
        if not action_type:
            return False, "Tipo de ação não especificado."

        act = action_type.upper()
        if act not in cls.SAFE_ACTIONS:
            return False, f"Ação '{action_type}' não permitida por razões de segurança."

        perm_level = cls.SAFE_ACTIONS[act]
        if perm_level in ["WRITE", "EXECUTE"] and not is_confirmed:
            return False, f"Ação '{act}' requer confirmação explícita do usuário."

        return True, "Ação validada com sucesso."

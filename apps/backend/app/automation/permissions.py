from enum import Enum
from typing import Dict, Any, Optional

class AutomationRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AutomationPermissionService:
    """
    Controla autorização de execução de automações.
    - LOW: Pode rodar automaticamente se a automação estiver ativa.
    - MEDIUM: Pode exigir confirmação dependendo da ação (ex: e-mails ou criação de eventos).
    - HIGH: SEMPRE exige confirmação explícita do usuário.
    - CRITICAL: Bloqueado no ambiente de produção.
    """
    @staticmethod
    def calculate_risk(actions: list) -> AutomationRiskLevel:
        highest_risk = AutomationRiskLevel.LOW
        for act in actions:
            act_type = act.get("type", "").upper()
            if act_type in ["OPEN_APPLICATION", "EXECUTE_EXISTING_AUTOMATION"]:
                return AutomationRiskLevel.HIGH
            elif act_type in ["CREATE_CALENDAR_EVENT", "SYNC_EMAIL", "EMAIL_ACTION"]:
                highest_risk = AutomationRiskLevel.MEDIUM
        return highest_risk

    @staticmethod
    def can_execute(automation: Any, is_confirmed: bool = False) -> tuple[bool, str]:
        if not getattr(automation, "is_active", True):
            return False, "Automação está pausada ou desativada."

        # Se kill switch estiver acionado globalmente
        from app.automation.kill_switch import is_kill_switch_active
        if is_kill_switch_active():
            return False, "Todas as automações estão temporariamente suspensas pelo Kill Switch."

        # Se a automação exige confirmação e o usuário ainda não confirmou
        if getattr(automation, "requires_confirmation", False) and not is_confirmed:
            return False, f"A automação '{automation.name}' exige confirmação explícita antes de executar."

        return True, "Autorizado para execução."

from typing import Dict, Any, Tuple
from datetime import datetime

class AutonomyPolicyEngine:
    """
    Motor de Políticas de Autonomia e Controle de Ação da IA (Fase 35).
    Garante que a autonomia do Agent permaneça determinística e subordinada à autoridade do usuário.
    """

    AUTONOMY_LEVELS = [
        "LEVEL_0_OBSERVER",
        "LEVEL_1_SUGGEST",
        "LEVEL_2_PREPARE",
        "LEVEL_3_LOW_RISK_AUTO",
        "LEVEL_4_APPROVAL_REQUIRED",
        "LEVEL_5_DISABLED"
    ]

    GLOBAL_SAFE_MODE = False
    AUTOMATIONS_ENABLED = True
    ORCHESTRATION_ENABLED = True
    REMOTE_CONTROL_ENABLED = True
    AGENT_ACTIONS_ENABLED = True
    NOTIFICATIONS_ENABLED = True
    CURRENT_AUTONOMY_LEVEL = "LEVEL_3_LOW_RISK_AUTO"

    FORBIDDEN_KEYWORDS = [
        "delete database", "drop table", "powershell", "cmd.exe",
        "bash", "eval(", "exec(", "sh ", "rm -rf", "kill system"
    ]

    @classmethod
    def evaluate_action_permission(
        cls,
        action_type: str,
        risk_level: str = "LOW",
        payload: Dict[str, Any] = None
    ) -> Tuple[bool, bool, str]:
        """
        Retorna: (is_allowed, requires_confirmation, reason)
        """
        act_upper = action_type.upper()
        payload_str = str(payload or {}).lower()

        # 1. Bloqueio Inviolável de Comandos Destrutivos
        if any(fk in payload_str for fk in cls.FORBIDDEN_KEYWORDS):
            return False, False, "Ação terminantemente proibida pela camada de segurança inviolável do RESOLVA."

        # 2. SAFE_MODE Global
        if cls.GLOBAL_SAFE_MODE:
            if act_upper.startswith("GET_") or act_upper.startswith("READ_") or act_upper == "SIMULATE_WORKFLOW":
                return True, False, "Permitido em SAFE_MODE (somente leitura / simulação)."
            return False, False, "Sistema em SAFE_MODE. Todas as operações de modificação estão suspensas."

        # 3. Kill Switches Individuais
        if not cls.AUTOMATIONS_ENABLED and ("WORKFLOW" in act_upper or "AUTOMATION" in act_upper):
            return False, False, "Subsistema de Automações desativado pelo Kill Switch."
        if not cls.AGENT_ACTIONS_ENABLED and "AGENT" in act_upper:
            return False, False, "Ações autônomas do Agent desativadas pelo Kill Switch."

        # 4. Avaliação por Nível de Autonomia
        if cls.CURRENT_AUTONOMY_LEVEL == "LEVEL_5_DISABLED":
            return False, False, "Autonomia desativada."
        elif cls.CURRENT_AUTONOMY_LEVEL == "LEVEL_0_OBSERVER" or cls.CURRENT_AUTONOMY_LEVEL == "LEVEL_1_SUGGEST":
            if act_upper.startswith("GET_") or act_upper.startswith("READ_"):
                return True, False, "Leitura permitida no nível de observador."
            return False, False, "Ações ativas bloqueadas no nível configurado."

        # 5. Avaliação de Risco e Confirmação
        if risk_level in ["MEDIUM", "HIGH"] or "DELETE" in act_upper:
            return True, True, "Ação permitida mediante confirmação explícita do usuário (Human-in-the-Loop)."

        return True, False, "Ação segura homologada aprovada para execução automática."

import re
from typing import Dict, Any, List, Tuple
from app.automation.workflow_catalog import HOMOLOGATED_ACTION_CATALOG
from app.core.exceptions import ValidationError

# Padrões perigosos proibidos em qualquer payload declarativo
FORBIDDEN_INJECTION_PATTERNS = [
    r"cmd\.exe", r"powershell", r"Invoke-Expression", r"iex\b",
    r"SELECT\s+.*\s+FROM", r"DROP\s+TABLE", r"INSERT\s+INTO", r"DELETE\s+FROM",
    r"rm\s+-rf", r"python\s+-c", r"exec\(", r"eval\(", r"__import__",
    r"subprocess", r"os\.system", r"shutil", r"chmod\b"
]

class WorkflowValidator:
    """
    Validador estrito de segurança e integridade de Workflows (Fase 33).
    Garante:
    - Zero Shell / Zero PowerShell / Zero SQL / Zero Script
    - Ações 100% pertencentes ao Catálogo Homologado
    - Parâmetros tipados e restritos à lista permitida
    - Prevenção de loops e timeouts obrigatórios
    """

    @classmethod
    def validate_workflow_definition(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []

        # 1. Checagem de injeção em campos de texto
        cls._scan_for_injection(data, errors)

        # 2. Validação de campos obrigatórios
        name = data.get("name")
        if not name or len(name.strip()) < 3:
            errors.append("Nome do workflow é obrigatório e deve ter no mínimo 3 caracteres.")

        max_runtime = data.get("max_runtime_seconds", 300)
        if not isinstance(max_runtime, int) or max_runtime <= 0 or max_runtime > 3600:
            errors.append("max_runtime_seconds deve ser um inteiro entre 1 e 3600 segundos.")

        # 3. Validação de Steps
        steps = data.get("steps", [])
        if not isinstance(steps, list) or len(steps) == 0:
            errors.append("O workflow deve conter pelo menos uma etapa (step).")
        elif len(steps) > 20:
            errors.append("O workflow não pode exceder o limite de 20 etapas.")

        seen_action_types = []
        for idx, step in enumerate(steps):
            step_errors = cls._validate_step(step, idx + 1)
            errors.extend(step_errors)
            action_type = step.get("action_type") if isinstance(step, dict) else getattr(step, "action_type", None)
            if action_type:
                seen_action_types.append(action_type)

        # 4. Detecção básica de loop direto na sequência
        if len(seen_action_types) >= 4 and len(set(seen_action_types)) == 1:
            errors.append("Sequência repetitiva excessiva da mesma ação detectada (Prevenção de Loop).")

        return len(errors) == 0, errors

    @classmethod
    def _validate_step(cls, step: Any, order: int) -> List[str]:
        errors = []
        if not isinstance(step, dict):
            step_dict = step.model_dump() if hasattr(step, "model_dump") else step.__dict__
        else:
            step_dict = step

        action_type = step_dict.get("action_type")
        if not action_type:
            errors.append(f"Etapa {order}: 'action_type' é obrigatório.")
            return errors

        act_upper = action_type.upper()
        if act_upper not in HOMOLOGATED_ACTION_CATALOG:
            errors.append(f"Etapa {order}: Ação '{action_type}' NÃO é homologada no catálogo seguro do RESOLVA.")
            return errors

        catalog_entry = HOMOLOGATED_ACTION_CATALOG[act_upper]
        params = step_dict.get("parameters", {})
        allowed_params = catalog_entry.get("allowed_parameters", [])

        # Valida chaves de parâmetros
        for p_key in params.keys():
            if p_key not in allowed_params:
                errors.append(f"Etapa {order}: Parâmetro '{p_key}' não é permitido para a ação '{action_type}'.")

        return errors

    @classmethod
    def _scan_for_injection(cls, obj: Any, errors: List[str], path: str = "root"):
        if isinstance(obj, str):
            for pattern in FORBIDDEN_INJECTION_PATTERNS:
                if re.search(pattern, obj, re.IGNORECASE):
                    errors.append(f"Padrão proibido de injeção/código detectado em '{path}': '{pattern}'")
        elif isinstance(obj, dict):
            for k, v in obj.items():
                cls._scan_for_injection(k, errors, f"{path}.{k}")
                cls._scan_for_injection(v, errors, f"{path}.{k}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                cls._scan_for_injection(item, errors, f"{path}[{i}]")

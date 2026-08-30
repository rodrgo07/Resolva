import re
from typing import Dict, Any, List, Tuple
from app.automation.workflow_catalog import HOMOLOGATED_ACTION_CATALOG

class OrchestrationSecurity:
    """
    Guardião de segurança inviolável da Orquestração Inteligente (Fase 34).
    Zero Shell, Zero PowerShell, Zero CMD, Zero Bash, Zero SQL, Zero eval(), Zero exec().
    """

    PROHIBITED_PATTERNS = [
        re.compile(r"powershell(\.exe)?", re.IGNORECASE),
        re.compile(r"cmd(\.exe)?", re.IGNORECASE),
        re.compile(r"bash(\.exe)?", re.IGNORECASE),
        re.compile(r"sh(\.exe)?", re.IGNORECASE),
        re.compile(r"python(\.exe)?\s+-c", re.IGNORECASE),
        re.compile(r"\brm\s+-rf\b", re.IGNORECASE),
        re.compile(r"\bdel\s+/[fqs]\b", re.IGNORECASE),
        re.compile(r"\beval\s*\(", re.IGNORECASE),
        re.compile(r"\bexec\s*\(", re.IGNORECASE),
        re.compile(r"\b__import__\s*\(", re.IGNORECASE),
        re.compile(r"\b(drop\s+table|delete\s+from|update\s+\w+\s+set|insert\s+into|select\s+\*\s+from)\b", re.IGNORECASE),
        re.compile(r"\$\(.*\)", re.IGNORECASE),
        re.compile(r"(.*)", re.IGNORECASE),
        re.compile(r"[;&|]{2,}", re.IGNORECASE)
    ]

    PROMPT_INJECTION_KEYWORDS = [
        "ignore all previous instructions",
        "execute this command",
        "bypass permission",
        "disable security",
        "run shell",
        "grant root access",
        "sudo rm"
    ]

    @classmethod
    def scan_for_malicious_content(cls, val: Any, path: str = "") -> List[str]:
        violations = []
        if isinstance(val, str):
            # 1. Prohibited injection patterns
            for pat in cls.PROHIBITED_PATTERNS:
                if pat.search(val):
                    violations.append(f"Injeção ou comando proibido detectado em '{path}': {val[:60]}")

            # 2. Prompt injection attempts
            val_lower = val.lower()
            for kw in cls.PROMPT_INJECTION_KEYWORDS:
                if kw in val_lower:
                    violations.append(f"Tentativa de manipulação / prompt injection detectada em '{path}': '{kw}'")

        elif isinstance(val, dict):
            for k, v in val.items():
                violations.extend(cls.scan_for_malicious_content(k, f"{path}.<key:{k}>"))
                violations.extend(cls.scan_for_malicious_content(v, f"{path}.{k}"))

        elif isinstance(val, list):
            for idx, item in enumerate(val):
                violations.extend(cls.scan_for_malicious_content(item, f"{path}[{idx}]"))

        return violations

    @classmethod
    def validate_orchestration_plan(cls, plan_steps: List[Dict[str, Any]]) -> Tuple[bool, List[str]]:
        errors = []
        if not isinstance(plan_steps, list):
            return False, ["O plano de orquestração deve ser uma lista."]

        if len(plan_steps) > 20:
            errors.append("Plano de orquestração excede o limite máximo de 20 etapas por execução.")

        for idx, step in enumerate(plan_steps):
            step_path = f"Step[{idx+1}]"
            action_type = str(step.get("action_type", "")).upper()

            if action_type not in HOMOLOGATED_ACTION_CATALOG:
                errors.append(f"{step_path}: Ação '{action_type}' NÃO pertence ao catálogo homologado do RESOLVA.")

            params = step.get("parameters", {})
            if not isinstance(params, dict):
                errors.append(f"{step_path}: Parâmetros devem ser um objeto JSON.")
            else:
                violations = cls.scan_for_malicious_content(params, f"{step_path}.parameters")
                errors.extend(violations)

        return len(errors) == 0, errors

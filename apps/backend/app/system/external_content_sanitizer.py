import re
from typing import Any, Dict, List, Tuple

class ExternalContentSanitizer:
    """
    Sanitizador de Entradas Externas e Blindagem Contra Prompt Injection (Fase 35).
    Garante que todo dado externo (e-mails, notas, tarefas, webhooks) seja tratado puramente como DADO e nunca como instrução executável.
    """

    INJECTION_PATTERNS = [
        re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
        re.compile(r"you\s+are\s+now\s+a\s+different\s+model", re.IGNORECASE),
        re.compile(r"system\s*:\s*admin", re.IGNORECASE),
        re.compile(r"<system_instructions>", re.IGNORECASE),
        re.compile(r"\b(powershell|cmd\.exe|bash|sh)\b", re.IGNORECASE),
        re.compile(r"\b(eval|exec|__import__)\b\s*\(", re.IGNORECASE),
        re.compile(r"\b(drop\s+table|delete\s+from|insert\s+into)\b", re.IGNORECASE),
        re.compile(r"bypass\s+security", re.IGNORECASE),
        re.compile(r"disable\s+safety", re.IGNORECASE)
    ]

    @classmethod
    def sanitize_input(cls, content: Any) -> Tuple[Any, bool]:
        """
        Retorna: (sanitized_content, was_injection_detected)
        """
        if isinstance(content, str):
            has_injection = any(pat.search(content) for pat in cls.INJECTION_PATTERNS)
            # Normalização de texto segura sem alterar caracteres válidos
            cleaned = content.replace("<script>", "").replace("</script>", "")
            return cleaned, has_injection
        elif isinstance(content, dict):
            clean_dict = {}
            detected = False
            for k, v in content.items():
                clean_v, d = cls.sanitize_input(v)
                clean_dict[k] = clean_v
                if d: detected = True
            return clean_dict, detected
        elif isinstance(content, list):
            clean_list = []
            detected = False
            for item in content:
                clean_item, d = cls.sanitize_input(item)
                clean_list.append(clean_item)
                if d: detected = True
            return clean_list, detected
        return content, False

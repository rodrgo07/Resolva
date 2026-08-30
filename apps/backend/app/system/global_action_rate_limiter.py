from datetime import datetime
from typing import Dict, List, Tuple

class GlobalActionRateLimiter:
    """
    Proteção Global Contra Loops, Spam de Notificações, Workflows e Comandos Remotos (Fase 35).
    """

    _COUNTERS: Dict[str, List[datetime]] = {}
    LIMITS = {
        "WORKFLOW_EXECUTE": (20, 60),    # máx 20 por 60s
        "SHOW_NOTIFICATION": (10, 60),   # máx 10 por 60s
        "REMOTE_COMMAND": (15, 60),      # máx 15 por 60s
        "ORCHESTRATION_RUN": (10, 60),   # máx 10 por 60s
        "DEFAULT": (30, 60)
    }

    @classmethod
    def check_rate_limit(cls, action_type: str, device_id: str = "DESKTOP-MAIN") -> Tuple[bool, str]:
        now = datetime.utcnow()
        key = f"{action_type.upper()}_{device_id}"
        max_count, window_sec = cls.LIMITS.get(action_type.upper(), cls.LIMITS["DEFAULT"])

        history = cls._COUNTERS.setdefault(key, [])
        # Limpa timestamps fora da janela
        cls._COUNTERS[key] = [t for t in history if (now - t).total_seconds() < window_sec]

        if len(cls._COUNTERS[key]) >= max_count:
            return False, f"Taxa limite excedida para '{action_type}' ({max_count} ops / {window_sec}s). Bloqueado por proteção anti-loop."

        cls._COUNTERS[key].append(now)
        return True, "OK"

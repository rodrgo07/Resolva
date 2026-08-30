import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional

class StructuredLogger:
    """
    Logger Estruturado com Redaction Automática de Segredos (Fase 35).
    Zero vazamento de passwords, tokens, API keys, credenciais OAuth.
    """

    REDACT_KEYS = {
        "password", "token", "access_token", "refresh_token",
        "authorization", "api_key", "secret", "client_secret",
        "private_key", "bearer"
    }

    def __init__(self):
        self.logger = logging.getLogger("resolva.structured")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(message)s')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    @classmethod
    def sanitize(cls, data: Any) -> Any:
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if any(sec in k.lower() for sec in cls.REDACT_KEYS):
                    sanitized[k] = "[REDACTED_SECRET]"
                else:
                    sanitized[k] = cls.sanitize(v)
            return sanitized
        elif isinstance(data, list):
            return [cls.sanitize(item) for item in data]
        elif isinstance(data, str):
            if re.search(r"bearer\s+[a-zA-Z0-9_\-\.]+", data, re.IGNORECASE):
                return re.sub(r"bearer\s+[a-zA-Z0-9_\-\.]+", "Bearer [REDACTED]", data, flags=re.IGNORECASE)
            return data
        return data

    def log(
        self,
        level: str,
        component: str,
        event: str,
        message: str,
        correlation_id: Optional[str] = None,
        device_id: str = "DESKTOP-MAIN",
        duration_ms: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": level.upper(),
            "component": component,
            "event": event,
            "message": message,
            "correlation_id": correlation_id,
            "device_id": device_id,
            "duration_ms": duration_ms,
            "details": self.sanitize(details or {})
        }

        json_str = json.dumps(payload, ensure_ascii=False)
        if level.upper() == "ERROR" or level.upper() == "CRITICAL":
            self.logger.error(json_str)
        elif level.upper() == "WARNING":
            self.logger.warning(json_str)
        else:
            self.logger.info(json_str)

structured_logger = StructuredLogger()

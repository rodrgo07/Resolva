from typing import Dict, Any
from datetime import datetime, time
from app.schemas.notification import NotificationPreferences

PRIORITY_LEVELS = {
    "LOW": 10,
    "NORMAL": 20,
    "IMPORTANT": 30,
    "URGENT": 40,
    "CRITICAL": 50
}

class NotificationPolicy:
    """
    Políticas de Notificação: Quiet Hours, Anti-Spam, Rate Limit e Filtro por Categoria.
    """
    def __init__(self, prefs: NotificationPreferences):
        self.prefs = prefs

    def is_source_enabled(self, source: str) -> bool:
        if not self.prefs.enabled:
            return False
        s = source.upper()
        if s == "TASKS" and not self.prefs.tasks_enabled:
            return False
        if s == "CALENDAR" and not self.prefs.calendar_enabled:
            return False
        if s == "EMAILS" and not self.prefs.emails_enabled:
            return False
        if s == "STUDIES" and not self.prefs.studies_enabled:
            return False
        if s == "FINANCES" and not self.prefs.finances_enabled:
            return False
        if s == "AUTOMATIONS" and not self.prefs.automations_enabled:
            return False
        if s == "AGENT" and not self.prefs.agent_enabled:
            return False
        return True

    def is_priority_allowed(self, priority: str) -> bool:
        req_level = PRIORITY_LEVELS.get(self.prefs.min_priority.upper(), 10)
        notif_level = PRIORITY_LEVELS.get(priority.upper(), 20)
        return notif_level >= req_level

    def is_in_quiet_hours(self, current_time: datetime | None = None) -> bool:
        if not self.prefs.quiet_hours_enabled:
            return False

        now = current_time or datetime.now()
        now_time = now.time()

        try:
            start_parts = [int(p) for p in self.prefs.quiet_hours_start.split(":")]
            end_parts = [int(p) for p in self.prefs.quiet_hours_end.split(":")]
            start_t = time(start_parts[0], start_parts[1])
            end_t = time(end_parts[0], end_parts[1])

            if start_t <= end_t:
                return start_t <= now_time <= end_t
            else:
                # Período noturno que cruza meia-noite (ex: 22:00 até 07:00)
                return now_time >= start_t or now_time <= end_t
        except Exception:
            return False

    def can_dispatch_toast(self, priority: str, current_time: datetime | None = None) -> bool:
        if not self.prefs.enabled or not self.prefs.windows_toast_enabled:
            return False

        p = priority.upper()
        if not self.is_priority_allowed(p):
            return False

        if self.is_in_quiet_hours(current_time):
            if p == "CRITICAL" and self.prefs.allow_critical_in_quiet_hours:
                return True
            return False

        return True

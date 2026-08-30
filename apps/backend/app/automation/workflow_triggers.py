from typing import Dict, Any, List, Optional
from datetime import datetime, time
import re

class WorkflowTriggersEngine:
    """
    Motor de Triggers de Workflows.
    Avalia eventos e agendamentos contra as regras de disparo declarativas.
    """

    @staticmethod
    def match_trigger(trigger_config: Dict[str, Any], event_type: str, event_payload: Dict[str, Any]) -> bool:
        if not trigger_config:
            return False

        trig_type = trigger_config.get("type", "").upper()

        # 1. Trigger Manual
        if trig_type == "MANUAL" and event_type == "MANUAL":
            return True

        # 2. Trigger por Evento do EventBus
        if trig_type in ["EVENT", "TASK_STATUS", "POMODORO", "SYNC", "CONNECTIVITY", "NOTIFICATION", "DEVICE"]:
            target_event = trigger_config.get("event")
            if target_event and target_event.upper() == event_type.upper():
                # Valida payload do evento se houver filtro adicional
                filters = trigger_config.get("payload_filter", {})
                for k, v in filters.items():
                    if event_payload.get(k) != v:
                        return False
                return True

        # 3. Trigger por Horário / Agendamento (TIME / SCHEDULE)
        if trig_type in ["TIME", "SCHEDULE"]:
            target_time = trigger_config.get("time") # '07:00'
            target_days = trigger_config.get("days", []) # ['MONDAY', 'TUESDAY'...]
            
            now = datetime.utcnow() # ou local time se passado no payload
            current_time_str = event_payload.get("time") or now.strftime("%H:%M")
            current_day_str = event_payload.get("day") or now.strftime("%A").upper()

            if target_time and target_time != current_time_str:
                return False

            if target_days and current_day_str not in [d.upper() for d in target_days]:
                return False

            return True

        # 4. Trigger por Recomendação do Agente
        if trig_type == "AGENT_RECOMMENDATION" and event_type == "AGENT_RECOMMENDATION_CREATED":
            return True

        return False

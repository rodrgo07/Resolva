from typing import Dict, Any, List
from app.ai.context_engine import ContextEngine

class PlanningEngine:
    """
    PlanningEngine do Resolva Agent.
    Transforma metas em etapas claras divididas em blocos de tempo com priorização racional.
    """
    def __init__(self, context_engine: ContextEngine):
        self.context_engine = context_engine

    async def generate_daily_plan(self, user_name: str = "Rodrigo") -> Dict[str, Any]:
        context = await self.context_engine.get_current_context(user_name)
        tasks = context.get("tasks_summary", {})
        calendar = context.get("calendar_summary", {})
        emails = context.get("emails_summary", {})

        high_priority = []
        med_priority = []
        time_blocks = []
        recommendations = []

        # 1. Tratar atrasos e urgências
        if tasks.get("overdue_count", 0) > 0:
            for ot in tasks.get("overdue_sample", []):
                high_priority.append(f"Resolver pendência atrasada: '{ot['title']}'")
            recommendations.append("Priorize tarefas com prazo estourado logo no primeiro bloco do dia.")

        # 2. E-mails prioritários
        if emails.get("important_unread_count", 0) > 0:
            high_priority.append(f"Triar {emails['important_unread_count']} e-mail(s) com prioridade alta ou urgente")
            time_blocks.append({"time": "09:00 - 09:30", "activity": "Revisão e resposta de e-mails prioritários"})

        # 3. Tarefas de hoje
        for tt in tasks.get("today_sample", []):
            med_priority.append(f"Executar: '{tt['title']}'")

        # 4. Blocos de tempo
        time_blocks.append({"time": "09:30 - 11:30", "activity": "Bloco de Foco: Tarefas Críticas e Desenvolvimento"})
        if calendar.get("events_count", 0) > 0:
            for ev in calendar.get("events", []):
                time_blocks.append({"time": "Compromisso Agendado", "activity": ev["title"]})
        else:
            time_blocks.append({"time": "14:00 - 16:00", "activity": "Bloco de Trabalho Contínuo & Alinhamentos"})

        time_blocks.append({"time": "16:30 - 17:30", "activity": "Sessão de Estudos & Aprendizado Focado"})

        return {
            "date": context.get("today_date"),
            "high_priority": high_priority,
            "medium_priority": med_priority,
            "time_blocks": time_blocks,
            "recommendations": recommendations or ["Mantenha pausas regulares entre blocos de foco."]
        }

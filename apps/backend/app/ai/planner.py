from typing import Dict, Any, List
from datetime import datetime
from app.ai.context_engine import ContextEngine
from app.ai.memory import AgentMemoryManager
from app.ai.prediction_engine import PredictionEngine

class PlanningEngine:
    """
    Fase 31: PlanningEngine Preditivo e Autônomo Seguro.
    Gera planos preditivos diários e semanais, detecta gargalos de tempo e
    sugere alocações otimizadas baseadas em previsões e padrões comportamentais.
    """
    def __init__(
        self, 
        context_engine: ContextEngine, 
        memory_manager: AgentMemoryManager = None,
        prediction_engine: PredictionEngine = None
    ):
        self.context_engine = context_engine
        self.memory_manager = memory_manager
        self.prediction_engine = prediction_engine

    async def generate_daily_plan(self, user_name: str = "Rodrigo") -> Dict[str, Any]:
        context = await self.context_engine.get_current_context(user_name)
        tasks = context.get("tasks_summary", {})
        calendar = context.get("calendar_summary", {})
        emails = context.get("emails_summary", {})

        predictions_data = {}
        if self.prediction_engine:
            try:
                predictions_data = await self.prediction_engine.generate_predictions()
            except Exception:
                pass

        high_priority = []
        med_priority = []
        time_blocks = []
        recommendations = list(predictions_data.get("proactive_recommendations", []))
        risk_warnings = list(predictions_data.get("risk_warnings", []))

        # 1. Tratar atrasos e urgências
        overdue_cnt = tasks.get("overdue_count", 0)
        if overdue_cnt > 0:
            for ot in tasks.get("overdue_sample", []):
                high_priority.append(f"Resolver pendência atrasada: '{ot['title']}'")

        # 2. E-mails prioritários
        if emails.get("important_unread_count", 0) > 0:
            high_priority.append(f"Triar {emails['important_unread_count']} e-mail(s) com prioridade alta ou urgente")
            time_blocks.append({"time": "09:00 - 09:30", "activity": "Revisão e resposta de e-mails prioritários", "type": "communication"})

        # 3. Tarefas de hoje
        for tt in tasks.get("today_sample", []):
            med_priority.append(f"Executar: '{tt['title']}'")

        # 4. Alocação Preditiva em Blocos de Foco (Baseado em horários de pico)
        focus_window = predictions_data.get("suggested_focus_window", "09:30 - 11:30")
        time_blocks.append({
            "time": focus_window,
            "activity": "Bloco de Foco Profundo: Tarefas Críticas",
            "type": "deep_work",
            "suggested_mode": "Pomodoro (25m)"
        })

        if calendar.get("events_count", 0) > 0:
            for ev in calendar.get("events", []):
                time_blocks.append({"time": "Compromisso Agendado", "activity": ev["title"], "type": "meeting"})
        else:
            time_blocks.append({"time": "14:00 - 16:00", "activity": "Bloco de Trabalho Contínuo & Alinhamentos", "type": "work"})

        time_blocks.append({"time": "16:30 - 17:30", "activity": "Sessão de Estudos & Aprendizado Focado", "type": "study"})

        if not recommendations:
            recommendations.append("Mantenha pausas regulares de 5 minutos a cada bloco de 25 minutos de foco.")

        return {
            "date": context.get("today_date"),
            "high_priority": high_priority,
            "medium_priority": med_priority,
            "time_blocks": time_blocks,
            "recommendations": recommendations,
            "risk_warnings": risk_warnings,
            "predictions_summary": predictions_data
        }

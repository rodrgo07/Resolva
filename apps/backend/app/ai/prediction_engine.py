from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.finance import Expense
from app.ai.pattern_engine import PatternEngine

class PredictionEngine:
    """
    Motor de Previsões Preditivas e Antecipação de Necessidades (Fase 31).
    Antecipa:
    - Riscos de atraso em tarefas com base no histórico
    - Gargalos de agenda e sobreposição de compromissos
    - Tendências de gastos vs orçamento
    - Melhores momentos para iniciar blocos de foco
    """
    def __init__(self, db: AsyncSession, pattern_engine: PatternEngine = None):
        self.db = db
        self.pattern_engine = pattern_engine or PatternEngine(db)

    async def generate_predictions(self) -> Dict[str, Any]:
        today = date.today()
        now = datetime.utcnow()
        patterns = await self.pattern_engine.analyze_productivity_patterns()

        # 1. Tarefas com alto risco de atraso
        stmt_overdue = select(Task).where(Task.status == "pendente", Task.due_date < today)
        res_overdue = await self.db.execute(stmt_overdue)
        overdue_tasks = res_overdue.scalars().all()

        stmt_today_tasks = select(Task).where(Task.status == "pendente", Task.due_date == today)
        res_today = await self.db.execute(stmt_today_tasks)
        today_tasks = res_today.scalars().all()

        # 2. Compromissos das próximas 24h
        stmt_events = select(CalendarEvent).where(
            CalendarEvent.start_time >= now,
            CalendarEvent.start_time <= now + timedelta(days=1)
        )
        res_events = await self.db.execute(stmt_events)
        upcoming_events = res_events.scalars().all()

        risk_warnings = []
        recommendations = []

        if len(overdue_tasks) > 0:
            risk_warnings.append({
                "type": "OVERDUE_ACCUMULATION",
                "severity": "HIGH",
                "message": f"Você tem {len(overdue_tasks)} tarefa(s) atrasada(s). Risco de sobrecarga no cronograma da semana.",
                "affected_items": [t.title for t in overdue_tasks[:3]]
            })
            recommendations.append("Alocar o primeiro bloco da manhã exclusivamente para liquidar pendências atrasadas.")

        if len(today_tasks) > 5:
            risk_warnings.append({
                "type": "DAILY_TASK_OVERLOAD",
                "severity": "MEDIUM",
                "message": f"{len(today_tasks)} tarefas planejadas para hoje excedem a capacidade recomendada (máx 4 prioritárias).",
                "affected_items": [t.title for t in today_tasks[:3]]
            })
            recommendations.append("Repriorizar 2 tarefas para o dia seguinte para evitar fadiga cognitiva.")

        if len(upcoming_events) >= 3:
            risk_warnings.append({
                "type": "CALENDAR_FRAGMENTATION",
                "severity": "MEDIUM",
                "message": "Agenda fragmentada com múltiplas reuniões. Pouco tempo contínuo para Deep Work.",
                "affected_items": [e.title for e in upcoming_events]
            })
            recommendations.append(f"Reservar bloco de foco protegido entre {patterns.get('best_focus_window', '09:00 - 11:30')}.")

        return {
            "prediction_timestamp": now.isoformat(),
            "productivity_score_estimate": patterns.get("tasks_completion_rate_pct", 85.0),
            "suggested_focus_window": patterns.get("best_focus_window", "09:00 - 11:30"),
            "risk_warnings": risk_warnings,
            "proactive_recommendations": recommendations or [
                "Cronograma balanceado. Mantenha o ritmo com pausas Pomodoro regulares."
            ],
            "patterns_summary": patterns
        }

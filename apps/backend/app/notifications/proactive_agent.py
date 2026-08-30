from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.schemas.notification import NotificationCreate
from app.core.logging import logger

class ProactiveAgent:
    """
    Agente Proativo do RESOLVA:
    Analisa o contexto diário e sugere ações de alto valor sem executar escritas destrutivas.
    Fluxo estrito: READ -> SUGGEST -> PREPARE -> CONFIRM -> WRITE.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def analyze_context_and_recommend(self) -> List[NotificationCreate]:
        recommendations = []
        now = datetime.now()
        today_date = date.today().isoformat()

        # 1. Cruzamento Tarefas Pendentes x Próximo Compromisso
        stmt_ev = select(CalendarEvent).where(
            CalendarEvent.start_time >= now
        ).order_by(CalendarEvent.start_time.asc()).limit(1)
        res_ev = await self.db.execute(stmt_ev)
        next_event = res_ev.scalar_one_or_none()

        stmt_pending = select(Task).where(
            Task.status != "concluida",
            Task.due_date == date.today()
        )
        res_pending = await self.db.execute(stmt_pending)
        pending_today = res_pending.scalars().all()

        if next_event:
            mins_to_event = int((next_event.start_time - now).total_seconds() / 60)
            if 15 <= mins_to_event <= 45 and len(pending_today) >= 1:
                recommendations.append(NotificationCreate(
                    type="AGENT_RECOMMENDATION",
                    title="Dica do Resolva Agent",
                    message=f"Você tem '{next_event.title}' em {mins_to_event} minutos e {len(pending_today)} tarefa(s) pendente(s) hoje. Posso ajudar a organizar?",
                    priority="IMPORTANT",
                    source="AGENT",
                    source_id=f"agent_rec_event_task_{next_event.id}",
                    action_type="NAVIGATE",
                    action_payload={"page": "ai"}
                ))

        # 2. Recomendação de Planejamento Matinal (08h às 10h)
        if 8 <= now.hour <= 10:
            recommendations.append(NotificationCreate(
                type="AGENT_RECOMMENDATION",
                title="Bom dia! Vamos planejar o seu dia?",
                message="Abra o Resolva Agent para ver suas prioridades, compromissos e tarefas do dia.",
                priority="NORMAL",
                source="AGENT",
                source_id=f"agent_rec_morning_{now.strftime('%Y%m%d')}",
                action_type="NAVIGATE",
                action_payload={"page": "ai"}
            ))

        return recommendations

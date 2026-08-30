from typing import Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.models.finance import Expense, TransactionType
from app.models.study import StudySession
from app.models.notification import Notification
from app.core.logging import logger

class ContextEngine:
    """
    ContextEngine do Resolva Agent.
    Gera resumos estruturados e compactos sob demanda, evitando sobrecarregar o LLM com dados brutos ou sensíveis.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_current_context(self, user_name: str = "Rodrigo") -> Dict[str, Any]:
        now = datetime.now()
        today = date.today()
        seven_days_ago = now - timedelta(days=7)

        # 1. Tarefas atrasadas e tarefas de hoje
        tasks_stmt = select(Task).where(
            and_(
                Task.status.in_([TaskStatus.pendente, TaskStatus.em_andamento]),
                Task.due_date <= today
            )
        ).limit(10)
        tasks_res = await self.db.execute(tasks_stmt)
        tasks = list(tasks_res.scalars().all())

        overdue_tasks = [t for t in tasks if t.due_date and t.due_date < today]
        today_tasks = [t for t in tasks if t.due_date and t.due_date == today]

        # 2. Compromissos e eventos de hoje
        cal_stmt = select(CalendarEvent).where(
            func.date(CalendarEvent.start_time) == today
        ).order_by(CalendarEvent.start_time.asc()).limit(5)
        cal_res = await self.db.execute(cal_stmt)
        events = list(cal_res.scalars().all())

        # 3. E-mails não lidos e prioritários
        emails_stmt = select(Email).where(
            and_(
                Email.is_read == False,
                Email.ai_classification.in_(["CRITICAL", "IMPORTANT", "urgente", "importante"])
            )
        ).order_by(Email.received_at.desc()).limit(5)
        emails_res = await self.db.execute(emails_stmt)
        important_emails = list(emails_res.scalars().all())

        # 4. Notificações não lidas
        notifs_stmt = select(Notification).where(Notification.is_read == False).limit(5)
        notifs_res = await self.db.execute(notifs_stmt)
        notifications = list(notifs_res.scalars().all())

        # 5. Progresso de estudos (últimos 7 dias)
        study_stmt = select(func.sum(StudySession.duration_minutes)).where(
            StudySession.started_at >= seven_days_ago
        )
        study_res = await self.db.execute(study_stmt)
        study_min = study_res.scalar() or 0

        return {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "today_date": today.strftime("%Y-%m-%d"),
            "user_name": user_name,
            "tasks_summary": {
                "overdue_count": len(overdue_tasks),
                "today_count": len(today_tasks),
                "overdue_sample": [{"id": t.id, "title": t.title, "priority": t.priority.value if hasattr(t.priority, "value") else str(t.priority)} for t in overdue_tasks[:3]],
                "today_sample": [{"id": t.id, "title": t.title, "due_time": str(t.due_time) if t.due_time else None} for t in today_tasks[:3]]
            },
            "calendar_summary": {
                "events_count": len(events),
                "events": [{"id": e.id, "title": e.title, "start_time": str(e.start_time)} for e in events]
            },
            "emails_summary": {
                "important_unread_count": len(important_emails),
                "emails": [{"id": em.id, "from": em.from_name or em.from_address, "subject": em.subject, "classification": em.ai_classification} for em in important_emails]
            },
            "studies_summary": {
                "minutes_last_7_days": study_min
            },
            "notifications_summary": {
                "unread_count": len(notifications),
                "items": [n.title for n in notifications[:3]]
            }
        }

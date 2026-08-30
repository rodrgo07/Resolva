from typing import List, Dict, Any
from datetime import datetime, timedelta, date
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.models.study import StudySession, StudySubject
from app.models.finance import Expense
from app.schemas.notification import NotificationCreate
from app.core.logging import logger

class TaskNotificationAnalyzer:
    @staticmethod
    async def analyze(db: AsyncSession) -> List[NotificationCreate]:
        notifications = []
        today_date = date.today()
        today_str = today_date.isoformat()

        # 1. Tarefas Atrasadas (Overdue)
        stmt_overdue = select(Task).where(
            Task.status != "concluida",
            Task.due_date < today_date
        )
        res_overdue = await db.execute(stmt_overdue)
        overdue_tasks = res_overdue.scalars().all()

        if len(overdue_tasks) == 1:
            t = overdue_tasks[0]
            priority = "URGENT" if str(t.priority).lower() in ["alta", "urgente"] else "IMPORTANT"
            notifications.append(NotificationCreate(
                type="TASK_OVERDUE",
                title="Tarefa Atrasada",
                message=f"A tarefa '{t.title}' está atrasada (vencimento: {t.due_date}).",
                priority=priority,
                source="TASKS",
                source_id=f"task_{t.id}",
                action_type="OPEN_TASK",
                action_payload={"task_id": t.id, "page": "tasks"}
            ))
        elif len(overdue_tasks) > 1:
            notifications.append(NotificationCreate(
                type="TASK_OVERDUE",
                title="Tarefas Atrasadas",
                message=f"Você possui {len(overdue_tasks)} tarefas atrasadas que precisam de atenção.",
                priority="URGENT",
                source="TASKS",
                source_id=f"tasks_overdue_batch_{today_str}",
                action_type="NAVIGATE",
                action_payload={"page": "tasks"}
            ))

        # 2. Tarefas vencendo hoje
        stmt_due_today = select(Task).where(
            Task.status != "concluida",
            Task.due_date == today_date
        )
        res_today = await db.execute(stmt_due_today)
        due_today_tasks = res_today.scalars().all()

        if due_today_tasks:
            notifications.append(NotificationCreate(
                type="REMINDER",
                title="Tarefas para Hoje",
                message=f"Você tem {len(due_today_tasks)} tarefa(s) programada(s) para vencer hoje.",
                priority="NORMAL",
                source="TASKS",
                source_id=f"tasks_due_today_{today_str}",
                action_type="NAVIGATE",
                action_payload={"page": "tasks"}
            ))

        return notifications


class CalendarNotificationAnalyzer:
    @staticmethod
    async def analyze(db: AsyncSession) -> List[NotificationCreate]:
        notifications = []
        now = datetime.now()
        in_30_min = now + timedelta(minutes=30)
        in_2_hours = now + timedelta(hours=2)

        # Eventos nas próximas 2 horas
        stmt = select(CalendarEvent).where(
            CalendarEvent.start_time >= now,
            CalendarEvent.start_time <= in_2_hours
        ).order_by(CalendarEvent.start_time.asc())
        res = await db.execute(stmt)
        events = res.scalars().all()

        for ev in events:
            diff_mins = int((ev.start_time - now).total_seconds() / 60)
            if diff_mins <= 15:
                priority = "CRITICAL"
                time_desc = f"em {max(1, diff_mins)} minutos"
            elif diff_mins <= 30:
                priority = "URGENT"
                time_desc = "em 30 minutos"
            else:
                priority = "IMPORTANT"
                time_desc = f"às {ev.start_time.strftime('%H:%M')}"

            notifications.append(NotificationCreate(
                type="CALENDAR_UPCOMING",
                title=f"Compromisso {time_desc}",
                message=f"'{ev.title}' começará {time_desc}.",
                priority=priority,
                source="CALENDAR",
                source_id=f"event_{ev.id}_{ev.start_time.strftime('%Y%m%d%H%M')}",
                action_type="OPEN_CALENDAR",
                action_payload={"event_id": ev.id, "page": "calendar"}
            ))

        return notifications


class EmailNotificationAnalyzer:
    @staticmethod
    async def analyze(db: AsyncSession) -> List[NotificationCreate]:
        notifications = []
        # Busca e-mails não lidos marcados como importantes ou urgentes pela IA
        stmt = select(Email).where(
            Email.is_read == False,
            Email.ai_classification.in_(["URGENT", "HIGH", "CRITICAL", "IMPORTANT"])
        ).order_by(Email.received_at.desc()).limit(10)
        res = await db.execute(stmt)
        important_emails = res.scalars().all()

        if len(important_emails) == 1:
            em = important_emails[0]
            priority = "URGENT" if em.ai_classification in ["URGENT", "CRITICAL"] else "IMPORTANT"
            sender = em.from_name or em.from_address
            notifications.append(NotificationCreate(
                type="EMAIL_IMPORTANT",
                title="E-mail Importante Recebido",
                message=f"De {sender}: '{em.subject}'",
                priority=priority,
                source="EMAILS",
                source_id=f"email_{em.id}",
                action_type="OPEN_EMAIL",
                action_payload={"email_id": em.id, "page": "emails"}
            ))
        elif len(important_emails) > 1:
            notifications.append(NotificationCreate(
                type="EMAIL_IMPORTANT",
                title="E-mails Importantes Aguardando",
                message=f"Você possui {len(important_emails)} e-mails prioritários na sua caixa de entrada.",
                priority="IMPORTANT",
                source="EMAILS",
                source_id=f"emails_batch_{len(important_emails)}",
                action_type="NAVIGATE",
                action_payload={"page": "emails"}
            ))

        return notifications


class StudyNotificationAnalyzer:
    @staticmethod
    async def analyze(db: AsyncSession) -> List[NotificationCreate]:
        notifications = []
        now = datetime.now()
        # Se for no meio da tarde/noite (ex: 15h ou 19h) e não houver sessões hoje
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        
        stmt = select(func.count(StudySession.id)).where(StudySession.started_at >= today_start)
        res = await db.execute(stmt)
        count_today = res.scalar() or 0

        if count_today == 0 and now.hour in [15, 19]:
            notifications.append(NotificationCreate(
                type="STUDY_REMINDER",
                title="Hora de Focar nos Estudos",
                message="Você ainda não realizou sessões de estudo hoje. Que tal um Pomodoro de 25 minutos?",
                priority="NORMAL",
                source="STUDIES",
                source_id=f"study_reminder_{now.strftime('%Y%m%d_%H')}",
                action_type="START_POMODORO",
                action_payload={"page": "studies"}
            ))

        return notifications


class FinanceNotificationAnalyzer:
    @staticmethod
    async def analyze(db: AsyncSession) -> List[NotificationCreate]:
        notifications = []
        now = datetime.now()
        # Se for início ou fim do dia (ex: 18h), emitir balanço informativo semanal se houver transações recentes
        if now.hour == 18 and now.weekday() == 4: # Sexta-feira às 18h
            notifications.append(NotificationCreate(
                type="FINANCE_ALERT",
                title="Resumo Financeiro da Semana",
                message="Verifique suas despesas e receitas registradas nesta semana.",
                priority="LOW",
                source="FINANCES",
                source_id=f"finance_weekly_{now.strftime('%Y%W')}",
                action_type="OPEN_FINANCES",
                action_payload={"page": "finances"}
            ))

        return notifications

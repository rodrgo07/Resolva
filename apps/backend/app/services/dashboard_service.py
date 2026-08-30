from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy import select, and_, or_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, TaskStatus, TaskPriority
from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.models.finance import Expense, TransactionType
from app.models.study import StudySession, StudySubject
from app.models.automation import Automation, AutomationExecution
from app.models.notification import Notification
from app.models.activity import ActivityLog
from app.ai.planner import PlanningEngine
from app.ai.context_engine import ContextEngine
from app.core.logging import logger

class DashboardService:
    """
    Serviço central de agregação e inteligência da Central de Comando do Resolva.
    Consolida métricas em lote, gera a timeline cronológica do dia e calcula a recomendação principal 'AGORA'.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_overview(self) -> Dict[str, Any]:
        now = datetime.now()
        today = date.today()
        seven_days_ago = now - timedelta(days=7)
        start_of_today = datetime.combine(today, datetime.min.time())

        # 1. Tarefas
        tasks_stmt = select(Task)
        tasks_res = await self.db.execute(tasks_stmt)
        all_tasks = tasks_res.scalars().all()

        pending_tasks = [t for t in all_tasks if t.status in [TaskStatus.pendente, TaskStatus.em_andamento]]
        overdue_tasks = [t for t in pending_tasks if t.due_date and t.due_date < today]
        completed_tasks = [t for t in all_tasks if t.status == TaskStatus.concluida]

        # 2. Agenda (Compromissos de hoje e próximo)
        cal_stmt = select(CalendarEvent).where(
            func.date(CalendarEvent.start_time) >= today
        ).order_by(CalendarEvent.start_time.asc())
        cal_res = await self.db.execute(cal_stmt)
        upcoming_events = cal_res.scalars().all()
        today_events = [e for e in upcoming_events if e.start_time.date() == today]
        next_event = upcoming_events[0] if upcoming_events else None

        # 3. E-mails (Gmail & Outlook unificados)
        email_unread_stmt = select(func.count(Email.id)).where(Email.is_read == False)
        email_crit_stmt = select(func.count(Email.id)).where(and_(Email.is_read == False, Email.ai_classification.in_(["CRITICAL", "urgente"])))
        email_imp_stmt = select(func.count(Email.id)).where(and_(Email.is_read == False, Email.ai_classification.in_(["IMPORTANT", "importante"])))
        
        unread_emails = (await self.db.execute(email_unread_stmt)).scalar() or 0
        critical_emails = (await self.db.execute(email_crit_stmt)).scalar() or 0
        important_emails = (await self.db.execute(email_imp_stmt)).scalar() or 0

        # 4. Estudos
        study_today_stmt = select(func.sum(StudySession.duration_minutes)).where(StudySession.started_at >= start_of_today)
        study_week_stmt = select(func.sum(StudySession.duration_minutes)).where(StudySession.started_at >= seven_days_ago)
        
        study_today_min = (await self.db.execute(study_today_stmt)).scalar() or 0
        study_week_min = (await self.db.execute(study_week_stmt)).scalar() or 0

        # 5. Finanças
        fin_today_stmt = select(func.sum(Expense.amount)).where(
            and_(Expense.type == TransactionType.expense, Expense.date == today)
        )
        fin_week_stmt = select(func.sum(Expense.amount)).where(
            and_(Expense.type == TransactionType.expense, Expense.date >= (today - timedelta(days=7)))
        )
        
        fin_today_val = (await self.db.execute(fin_today_stmt)).scalar() or 0.0
        fin_week_val = (await self.db.execute(fin_week_stmt)).scalar() or 0.0

        # 6. Automações
        auto_stmt = select(func.count(Automation.id)).where(Automation.is_active == True)
        active_autos = (await self.db.execute(auto_stmt)).scalar() or 0

        return {
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
            "today_date": today.strftime("%Y-%m-%d"),
            "tasks": {
                "total": len(all_tasks),
                "pending": len(pending_tasks),
                "overdue": len(overdue_tasks),
                "completed": len(completed_tasks),
            },
            "calendar": {
                "events_today_count": len(today_events),
                "next_event": {
                    "id": next_event.id,
                    "title": next_event.title,
                    "start_time": next_event.start_time.strftime("%H:%M"),
                    "start_date": next_event.start_time.strftime("%d/%m")
                } if next_event else None
            },
            "emails": {
                "unread_count": unread_emails,
                "critical_count": critical_emails,
                "important_count": important_emails
            },
            "studies": {
                "minutes_today": study_today_min,
                "hours_today": round(study_today_min / 60.0, 1),
                "hours_week": round(study_week_min / 60.0, 1)
            },
            "finances": {
                "expense_today": float(fin_today_val),
                "expense_week": float(fin_week_val)
            },
            "automations": {
                "active_count": active_autos
            }
        }

    async def get_now_card(self) -> Dict[str, Any]:
        """
        Determina o foco de ação mais crítico e imediato para o usuário no momento.
        """
        overview = await self.get_overview()
        tasks = overview["tasks"]
        emails = overview["emails"]
        calendar = overview["calendar"]
        studies = overview["studies"]

        # Prioridade 1: Tarefas Atrasadas
        if tasks["overdue"] > 0:
            return {
                "type": "overdue_tasks",
                "badge": "Atenção Imediata",
                "title": f"Você possui {tasks['overdue']} tarefa(s) atrasada(s)",
                "description": "Resolver pendências vencidas evita acúmulo e mantém seu dia sob controle.",
                "action_label": "Ver Tarefas Atrasadas",
                "action_target": "tasks",
                "priority_level": "critical"
            }

        # Prioridade 2: E-mails Críticos Não Lidos
        if emails["critical_count"] > 0:
            return {
                "type": "critical_emails",
                "badge": "E-mail Urgente",
                "title": f"{emails['critical_count']} e-mail(s) urgente(s) aguardando resposta",
                "description": "Mensagens prioritárias detectadas pela triagem de IA do Resolva.",
                "action_label": "Abrir Caixa de Entrada",
                "action_target": "emails",
                "priority_level": "high"
            }

        # Prioridade 3: Próximo Compromisso Próximo
        if calendar.get("next_event"):
            ev = calendar["next_event"]
            return {
                "type": "upcoming_event",
                "badge": "Próximo Compromisso",
                "title": f"{ev['title']} às {ev['start_time']}",
                "description": "Prepare-se para o seu compromisso agendado no calendário.",
                "action_label": "Ver Calendário",
                "action_target": "calendar",
                "priority_level": "medium"
            }

        # Prioridade 4: Estudo do Dia
        if studies["hours_today"] < 0.5:
            return {
                "type": "study_routine",
                "badge": "Foco & Aprendizado",
                "title": "Hora de avançar nos seus estudos",
                "description": "Inicie um bloco Pomodoro de 25 minutos para manter a consistência da semana.",
                "action_label": "Iniciar Pomodoro",
                "action_target": "studies",
                "priority_level": "normal"
            }

        # Estado Padrão: Produtividade Concluída / Livre
        return {
            "type": "all_clear",
            "badge": "Tudo em Dia",
            "title": "Nenhuma urgência pendente no momento",
            "description": "Seu dia está organizado. Aproveite para planejar novas metas ou descansar.",
            "action_label": "Organizar Meu Dia",
            "action_target": "ai",
            "priority_level": "low"
        }

    async def get_timeline(self) -> List[Dict[str, Any]]:
        """
        Gera a timeline cronológica do dia agregando eventos, tarefas, atividades e rotinas executadas.
        """
        today = date.today()
        start_dt = datetime.combine(today, datetime.min.time())
        end_dt = datetime.combine(today, datetime.max.time())
        timeline_items = []

        # 1. Eventos da Agenda
        cal_stmt = select(CalendarEvent).where(
            and_(CalendarEvent.start_time >= start_dt, CalendarEvent.start_time <= end_dt)
        ).order_by(CalendarEvent.start_time.asc())
        cal_res = await self.db.execute(cal_stmt)
        for ev in cal_res.scalars().all():
            timeline_items.append({
                "time": ev.start_time.strftime("%H:%M"),
                "raw_time": ev.start_time,
                "category": "calendar",
                "title": ev.title,
                "description": ev.description or "Compromisso na agenda",
                "icon": "calendar"
            })

        # 2. Tarefas com Prazo Hoje
        task_stmt = select(Task).where(Task.due_date == today)
        task_res = await self.db.execute(task_stmt)
        for t in task_res.scalars().all():
            time_str = t.due_time.strftime("%H:%M") if t.due_time else "Hoje"
            timeline_items.append({
                "time": time_str,
                "raw_time": datetime.combine(today, t.due_time) if t.due_time else start_dt,
                "category": "task",
                "title": t.title,
                "description": f"Prioridade: {t.priority.value if hasattr(t.priority, 'value') else t.priority} | Status: {t.status.value if hasattr(t.status, 'value') else t.status}",
                "icon": "check-square"
            })

        # 3. Atividades do Agent / Automações de Hoje
        act_stmt = select(ActivityLog).where(ActivityLog.created_at >= start_dt).order_by(ActivityLog.created_at.asc()).limit(10)
        act_res = await self.db.execute(act_stmt)
        for act in act_res.scalars().all():
            timeline_items.append({
                "time": act.created_at.strftime("%H:%M"),
                "raw_time": act.created_at,
                "category": "agent",
                "title": act.action,
                "description": act.description,
                "icon": "zap"
            })

        # Ordena cronologicamente
        timeline_items.sort(key=lambda x: x["raw_time"])
        for item in timeline_items:
            del item["raw_time"]

        # Se não houver itens suficientes, inclui marcos padrão
        if not timeline_items:
            timeline_items = [
                {"time": "08:00", "category": "system", "title": "Início da jornada diária", "description": "Sistema pronto", "icon": "clock"},
                {"time": "12:00", "category": "system", "title": "Alinhamento do meio-dia", "description": "Revisão de tarefas pendentes", "icon": "clock"},
                {"time": "18:00", "category": "system", "title": "Encerramento e revisão do dia", "description": "Resumo de produtividade", "icon": "clock"}
            ]

        return timeline_items

    async def get_recommendations(self) -> List[Dict[str, Any]]:
        overview = await self.get_overview()
        recs = []

        if overview["tasks"]["overdue"] > 0:
            recs.append({
                "id": "rec_overdue",
                "type": "tasks",
                "title": "Resolver Tarefas Atrasadas",
                "message": f"Você possui {overview['tasks']['overdue']} tarefa(s) que já ultrapassaram o prazo.",
                "action": "Ver Tarefas",
                "target": "tasks",
                "variant": "destructive"
            })

        if overview["emails"]["unread_count"] > 0:
            recs.append({
                "id": "rec_emails",
                "type": "emails",
                "title": "Revisar Caixa de Entrada",
                "message": f"Existem {overview['emails']['unread_count']} e-mail(s) não lidos no Gmail e Outlook.",
                "action": "Abrir E-mails",
                "target": "emails",
                "variant": "warning"
            })

        if overview["studies"]["hours_today"] < 1.0:
            recs.append({
                "id": "rec_studies",
                "type": "studies",
                "title": "Meta de Estudos Semanal",
                "message": f"Você acumulou {overview['studies']['hours_week']}h nesta semana. Que tal estudar 25min agora?",
                "action": "Iniciar Estudo",
                "target": "studies",
                "variant": "info"
            })

        if overview["finances"]["expense_week"] > 0:
            recs.append({
                "id": "rec_finances",
                "type": "finances",
                "title": "Controle Financeiro",
                "message": f"Total de R$ {overview['finances']['expense_week']:.2f} em despesas registradas nos últimos 7 dias.",
                "action": "Ver Gastos",
                "target": "finances",
                "variant": "secondary"
            })

        return recs

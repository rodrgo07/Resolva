from typing import Dict, Any, List, Optional
from datetime import datetime, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.models.study import StudySession
from app.models.workflow import Workflow
from app.schemas.orchestration import WorkflowCandidate

class WorkflowSelector:
    """
    Motor de Seleção Contextual e Scoring Determinístico de Workflows (Fase 34).
    Calcula pontuação explicável com pesos configuráveis sem números mágicos espalhados.
    """

    DEFAULT_WEIGHTS = {
        "urgency_weight": 30.0,
        "deadline_weight": 25.0,
        "contextual_weight": 20.0,
        "routine_weight": 15.0,
        "prediction_weight": 10.0,
        "interruption_penalty": 15.0
    }

    def __init__(self, db: AsyncSession, weights: Optional[Dict[str, float]] = None):
        self.db = db
        self.weights = {**self.DEFAULT_WEIGHTS, **(weights or {})}

    async def evaluate_candidates(self, context_override: Optional[Dict[str, Any]] = None) -> List[WorkflowCandidate]:
        now = datetime.now()
        candidates: List[WorkflowCandidate] = []

        # 1. Coleta de Contexto Operacional
        tasks_stmt = select(Task).where(Task.status != "concluida")
        tasks_res = await self.db.execute(tasks_stmt)
        active_tasks = tasks_res.scalars().all()

        today_date = now.date()
        overdue_tasks = []
        for t in active_tasks:
            if t.due_date:
                t_date = t.due_date if isinstance(t.due_date, type(today_date)) else getattr(t.due_date, 'date', lambda: t.due_date)()
                if t_date < today_date:
                    overdue_tasks.append(t)

        urgent_tasks = [t for t in active_tasks if getattr(t, "priority", "MEDIA").upper() == "ALTA"]

        events_stmt = select(CalendarEvent).where(CalendarEvent.start_time >= now.replace(hour=0, minute=0, second=0))
        events_res = await self.db.execute(events_stmt)
        today_events = events_res.scalars().all()

        upcoming_meetings = []
        for e in today_events:
            if e.start_time:
                st = e.start_time if isinstance(e.start_time, datetime) else datetime.combine(e.start_time, datetime.min.time())
                if 0 <= (st - now).total_seconds() <= 3600:
                    upcoming_meetings.append(e)


        # 2. Carrega Workflows Ativos
        from sqlalchemy.orm import selectinload
        wf_stmt = select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.enabled == True)
        wf_res = await self.db.execute(wf_stmt)
        active_workflows = wf_res.scalars().all()

        for wf in active_workflows:
            candidate = self._score_workflow(
                workflow=wf,
                now=now,
                overdue_count=len(overdue_tasks),
                urgent_count=len(urgent_tasks),
                upcoming_meetings=upcoming_meetings,
                total_active_tasks=len(active_tasks)
            )
            if candidate and candidate.score >= 40.0:
                candidates.append(candidate)

        # Ordena candidatos por pontuação decrescente
        candidates.sort(key=lambda c: c.score, reverse=True)
        return candidates

    def _score_workflow(
        self,
        workflow: Workflow,
        now: datetime,
        overdue_count: int,
        urgent_count: int,
        upcoming_meetings: List[CalendarEvent],
        total_active_tasks: int
    ) -> Optional[WorkflowCandidate]:
        score = 0.0
        factors = []
        name_lower = workflow.name.lower()

        # A) Planejamento Matinal
        if "matinal" in name_lower or "planejamento" in name_lower:
            if 6 <= now.hour <= 11:
                score += self.weights["routine_weight"] * 2.0
                factors.append(f"Horário matinal propício para planejamento ({now.strftime('%H:%M')}).")
            if total_active_tasks > 0:
                score += self.weights["contextual_weight"] * 1.5
                factors.append(f"{total_active_tasks} tarefas ativas na fila do dia.")

        # B) Preparação para Reunião
        elif "reunião" in name_lower or "reuniao" in name_lower:
            if upcoming_meetings:
                next_meet = upcoming_meetings[0]
                minutes_left = int((next_meet.start_time - now).total_seconds() / 60)
                score += self.weights["urgency_weight"] * 2.5
                factors.append(f"Reunião '{next_meet.title}' agendada para daqui a {minutes_left} minutos.")
            else:
                score -= self.weights["interruption_penalty"]

        # C) Alerta de Tarefas Atrasadas / Foco Urgente
        elif "atrasad" in name_lower or "urgente" in name_lower:
            if overdue_count > 0:
                score += self.weights["deadline_weight"] * 2.0 + (overdue_count * 5.0)
                factors.append(f"Detectadas {overdue_count} tarefas com prazo vencido pendentes.")
            if urgent_count > 0:
                score += self.weights["urgency_weight"] * 1.5
                factors.append(f"{urgent_count} tarefas de prioridade ALTA aguardando resolução.")

        # D) Rotina de Foco / Estudo
        elif "foco" in name_lower or "estudo" in name_lower or "pomodoro" in name_lower:
            if not upcoming_meetings:
                score += self.weights["contextual_weight"] * 2.0
                factors.append("Janela livre identificada na agenda (sem reuniões nos próximos 60 min).")
            else:
                score -= self.weights["interruption_penalty"] * 1.5
                factors.append("Janela curta devido a compromissos iminentes.")

        # Base score padrão
        if not factors:
            score += 35.0
            factors.append("Workflow disponível no catálogo ativo do usuário.")

        requires_conf = any(s.requires_confirmation for s in (workflow.steps or []))

        return WorkflowCandidate(
            workflow_id=workflow.workflow_id,
            name=workflow.name,
            score=round(score, 1),
            confidence=min(98, int(60 + (score * 0.4))),
            priority="URGENT" if score > 80 else "HIGH" if score > 60 else "NORMAL",
            required_confirmation=requires_conf,
            estimated_duration_seconds=sum((s.timeout_seconds or 60) for s in (workflow.steps or [])),
            expected_outcome=f"Execução das {len(workflow.steps or [])} etapas configuradas para {workflow.name}.",
            reason=f"Pontuação {round(score, 1)} calculada com base no contexto operacional atual.",
            factors=factors,
            action_preview=[s.action_type for s in (workflow.steps or [])]
        )

import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from sqlalchemy.orm import selectinload

from app.models.orchestration import (
    OrchestrationRun, WorkflowEventRule, WorkflowDependency,
    WorkflowFeedbackModel, WorkflowExplanationModel
)
from app.models.workflow import Workflow, WorkflowExecution
from app.automation.workflow_engine import WorkflowEngine
from app.automation.workflow_selector import WorkflowSelector
from app.automation.orchestration_security import OrchestrationSecurity
from app.automation.workflow_recovery import WorkflowRecoveryEngine
from app.automation.event_rules import EventRulesEngine
from app.services.event_bus import event_bus
from app.core.exceptions import ValidationError, NotFoundError, PermissionError

class OrchestrationEngine:
    """
    Orquestrador Central e Adaptativo do RESOLVA (Fase 34).
    Coordena seleção de workflows, montagem de planos, encadeamento, simulação Dry Run,
    recuperação contra falhas e confirmação human-in-the-loop.
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self.wf_engine = WorkflowEngine(db)
        self.selector = WorkflowSelector(db)
        self.rules_engine = EventRulesEngine(db)

    async def get_status(self) -> Dict[str, Any]:
        """
        Retorna o estado operacional do Orchestration Engine.
        """
        stmt_active = select(func.count(OrchestrationRun.id)).where(OrchestrationRun.status == "RUNNING")
        res_active = await self.db.execute(stmt_active)
        active_count = res_active.scalar() or 0

        stmt_pending = select(func.count(OrchestrationRun.id)).where(OrchestrationRun.status == "WAITING_CONFIRMATION")
        res_pending = await self.db.execute(stmt_pending)
        pending_count = res_pending.scalar() or 0

        return {
            "orchestrator_status": "OPERATIONAL",
            "active_runs": active_count,
            "waiting_confirmations": pending_count,
            "security_mode": "STRICT_PERMISSION_LAYER",
            "timestamp": datetime.utcnow().isoformat()
        }

    async def plan_and_simulate(
        self,
        workflow_ids: Optional[List[str]] = None,
        context_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Simula a execução de orquestração (Dry Run) sem aplicar alterações no banco.
        """
        candidates = await self.selector.evaluate_candidates(context_override)
        selected = [c for c in candidates if not workflow_ids or c.workflow_id in workflow_ids]

        plan_steps = []
        for cand in selected:
            wf = await self.wf_engine.get_workflow(cand.workflow_id)
            if wf:
                for step in (wf.steps or []):
                    plan_steps.append({
                        "workflow_id": wf.workflow_id,
                        "workflow_name": wf.name,
                        "action_type": step.action_type,
                        "parameters": step.parameters,
                        "permission_level": step.permission_level,
                        "requires_confirmation": step.requires_confirmation
                    })

        # Validação de Segurança
        is_safe, sec_errors = OrchestrationSecurity.validate_orchestration_plan(plan_steps)
        if not is_safe:
            raise ValidationError(f"Violação de segurança na simulação: {'; '.join(sec_errors)}")

        return {
            "is_dry_run": True,
            "total_workflows": len(selected),
            "total_steps": len(plan_steps),
            "workflows": [s.model_dump() for s in selected],
            "plan_steps": plan_steps,
            "estimated_duration_seconds": sum(c.estimated_duration_seconds for c in selected),
            "requires_user_confirmation": any(s["requires_confirmation"] for s in plan_steps)
        }

    async def run_orchestration(
        self,
        trigger_type: str = "MANUAL",
        trigger_source: str = "USER",
        device_id: str = "DESKTOP-MAIN",
        is_dry_run: bool = False,
        workflow_ids: Optional[List[str]] = None,
        context_override: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None
    ) -> OrchestrationRun:
        """
        Inicia e executa a orquestração de workflows.
        """
        # 1. Idempotência
        if idempotency_key:
            stmt = select(OrchestrationRun).where(OrchestrationRun.idempotency_key == idempotency_key)
            res = await self.db.execute(stmt)
            existing = res.scalar_one_or_none()
            if existing:
                return existing

        # 2. Seleção de Workflows
        candidates = await self.selector.evaluate_candidates(context_override)
        if workflow_ids:
            target_candidates = [c for c in candidates if c.workflow_id in workflow_ids]
        else:
            target_candidates = candidates[:3] # Top 3 prioritários

        if not target_candidates:
            # Fallback: Busca workflows ativos normais
            all_wf = await self.wf_engine.list_workflows(status="ACTIVE")
            if workflow_ids:
                all_wf = [w for w in all_wf if w.workflow_id in workflow_ids]
            if not all_wf:
                raise NotFoundError("Nenhum workflow ativo ou elegível para orquestração.")

        # 3. Montagem do Plano
        run_id = f"orch_{uuid.uuid4().hex[:10]}"
        correlation_id = f"corr_{uuid.uuid4().hex[:8]}"

        plan_snapshot = []
        for cand in target_candidates:
            wf = await self.wf_engine.get_workflow(cand.workflow_id)
            if wf:
                for step in (wf.steps or []):
                    plan_snapshot.append({
                        "workflow_id": wf.workflow_id,
                        "workflow_name": wf.name,
                        "step_id": step.step_id,
                        "order": step.order,
                        "action_type": step.action_type,
                        "parameters": step.parameters,
                        "permission_level": step.permission_level,
                        "requires_confirmation": step.requires_confirmation
                    })

        # Validação de Segurança
        is_safe, sec_errors = OrchestrationSecurity.validate_orchestration_plan(plan_snapshot)
        if not is_safe:
            raise ValidationError(f"Orquestração bloqueada por segurança: {'; '.join(sec_errors)}")

        run = OrchestrationRun(
            run_id=run_id,
            status="RUNNING",
            trigger_type=trigger_type,
            trigger_source=trigger_source,
            device_id=device_id,
            correlation_id=correlation_id,
            idempotency_key=idempotency_key,
            is_dry_run=is_dry_run,
            total_steps=len(plan_snapshot),
            completed_steps=0,
            plan_snapshot=plan_snapshot,
            context_snapshot=context_override or {},
            metrics={"started_at": datetime.utcnow().isoformat()}
        )
        self.db.add(run)

        # Registra Explicações para cada Workflow Selecionado
        for cand in target_candidates:
            expl = WorkflowExplanationModel(
                explanation_id=f"expl_{uuid.uuid4().hex[:8]}",
                orchestration_run_id=run_id,
                workflow_id=cand.workflow_id,
                title=f"Seleção de {cand.name}",
                reason=cand.reason,
                factors=cand.factors,
                confidence=cand.confidence,
                source_data={"score": cand.score, "priority": cand.priority}
            )
            self.db.add(expl)

        await self.db.commit()

        await event_bus.publish("ORCHESTRATION_STARTED", {
            "run_id": run_id,
            "total_steps": len(plan_snapshot),
            "is_dry_run": is_dry_run
        })

        # 4. Execução Sequencial com Dependências e Human-in-the-Loop
        completed = 0
        for cand in target_candidates:
            wf_exec = await self.wf_engine.execute_workflow(
                workflow_id=cand.workflow_id,
                trigger_source="ORCHESTRATOR",
                device_id=device_id,
                dry_run=is_dry_run,
                context_override=context_override,
                correlation_id=correlation_id
            )

            if wf_exec.status == "WAITING_CONFIRMATION":
                run.status = "WAITING_CONFIRMATION"
                await self.db.commit()
                await event_bus.publish("WORKFLOW_WAITING_CONFIRMATION", {
                    "run_id": run_id,
                    "workflow_id": cand.workflow_id
                })
                return await self.get_run(run_id)

            elif wf_exec.status == "FAILED":
                run.status = "FAILED"
                run.error = f"Falha no workflow '{cand.name}': {wf_exec.error}"
                run.finished_at = datetime.utcnow()
                await self.db.commit()
                await event_bus.publish("ORCHESTRATION_FAILED", {"run_id": run_id, "error": run.error})
                return await self.get_run(run_id)

            completed += len(wf_exec.step_executions or [])
            run.completed_steps = completed

        run.status = "COMPLETED"
        run.finished_at = datetime.utcnow()
        await self.db.commit()

        await event_bus.publish("ORCHESTRATION_COMPLETED", {"run_id": run_id, "completed_steps": completed})
        return await self.get_run(run_id)

    async def get_run(self, run_id: str) -> Optional[OrchestrationRun]:
        stmt = select(OrchestrationRun).options(
            selectinload(OrchestrationRun.explanations),
            selectinload(OrchestrationRun.feedbacks)
        ).where(OrchestrationRun.run_id == run_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def list_runs(self, limit: int = 20) -> List[OrchestrationRun]:
        stmt = select(OrchestrationRun).options(
            selectinload(OrchestrationRun.explanations),
            selectinload(OrchestrationRun.feedbacks)
        ).order_by(desc(OrchestrationRun.created_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def register_feedback(
        self,
        workflow_id: str,
        user_action: str,
        run_id: Optional[str] = None,
        reason: Optional[str] = None,
        device_id: str = "DESKTOP-MAIN"
    ) -> WorkflowFeedbackModel:
        feedback = WorkflowFeedbackModel(
            feedback_id=f"fb_{uuid.uuid4().hex[:8]}",
            orchestration_run_id=run_id,
            workflow_id=workflow_id,
            user_action=user_action.upper(),
            reason=reason,
            device_id=device_id
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        return feedback

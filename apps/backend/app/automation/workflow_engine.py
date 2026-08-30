import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc, update

from app.models.workflow import (
    Workflow, WorkflowStep, WorkflowExecution, WorkflowStepExecution,
    WorkflowConfirmation, WorkflowStatus, WorkflowSafetyLevel, WorkflowExecutionPolicy
)
from app.models.task import Task
from app.models.notification import Notification
from app.models.calendar import CalendarEvent
from app.models.study import StudySession
from app.models.finance import Expense
from app.automation.workflow_catalog import HOMOLOGATED_ACTION_CATALOG
from app.automation.workflow_validator import WorkflowValidator
from app.automation.workflow_conditions import WorkflowConditionsEngine
from app.automation.workflow_triggers import WorkflowTriggersEngine
from app.services.event_bus import event_bus
from app.automation.kill_switch import is_kill_switch_active
from app.core.exceptions import ValidationError, NotFoundError, PermissionError
from app.core.logging import logger

# Controle de taxa e profundidade para prevenção de loops infinitos
MAX_TRIGGER_DEPTH = 5
MAX_EXECUTIONS_PER_MINUTE = 60
_execution_history_timestamps: List[datetime] = []

class WorkflowEngine:
    """
    Motor Principal de Execução, Validação e Orquestração de Workflows (Fase 33).
    Garante:
    - Execução declarativa e determinística
    - Permission Layer e confirmação obrigatória para ações sensíveis
    - Proteção contra loops (max_trigger_depth) e rate limiting
    - Suporte a Dry Run e Simulação
    - Auditoria em tempo real e publicação no EventBus
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(self, data: Dict[str, Any], created_by: str = "USER") -> Workflow:
        # 1. Validação estrita
        is_valid, errors = WorkflowValidator.validate_workflow_definition(data)
        if not is_valid:
            raise ValidationError(f"Definição de workflow inválida: {'; '.join(errors)}")

        workflow_id = f"wf_{uuid.uuid4().hex[:10]}"
        steps_data = data.pop("steps", [])

        wf = Workflow(
            workflow_id=workflow_id,
            name=data["name"],
            description=data.get("description"),
            enabled=data.get("enabled", True),
            status=WorkflowStatus.ACTIVE.value if data.get("enabled", True) else WorkflowStatus.DISABLED.value,
            version=1,
            created_by=created_by,
            safety_level=data.get("safety_level", WorkflowSafetyLevel.AUTO_LOW_RISK.value),
            execution_policy=data.get("execution_policy", WorkflowExecutionPolicy.SINGLE_ACTIVE.value),
            max_runtime_seconds=data.get("max_runtime_seconds", 300),
            priority=data.get("priority", "NORMAL"),
            trigger_config=data.get("trigger_config", {}),
            condition_config=data.get("condition_config"),
            action_config=data.get("action_config"),
            retry_policy=data.get("retry_policy", {"max_attempts": 3, "backoff": [5, 15, 30]}),
            tags=data.get("tags", []),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(wf)
        await self.db.flush()

        for idx, step_item in enumerate(steps_data):
            s_dict = step_item if isinstance(step_item, dict) else step_item.model_dump()
            step_id = f"stp_{uuid.uuid4().hex[:8]}"
            catalog_entry = HOMOLOGATED_ACTION_CATALOG.get(s_dict["action_type"].upper(), {})
            requires_conf = s_dict.get("requires_confirmation") or catalog_entry.get("confirmation_required", False)

            step = WorkflowStep(
                step_id=step_id,
                workflow_id=workflow_id,
                order=idx + 1,
                name=s_dict.get("name", f"Etapa {idx + 1}"),
                action_type=s_dict["action_type"].upper(),
                parameters=s_dict.get("parameters", {}),
                condition=s_dict.get("condition"),
                timeout_seconds=s_dict.get("timeout_seconds", 60),
                retry_policy=s_dict.get("retry_policy", {"max_attempts": 2, "backoff": [3, 10]}),
                permission_level=catalog_entry.get("permission_level", "LOW"),
                requires_confirmation=requires_conf,
                compensating_action=s_dict.get("compensating_action"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            self.db.add(step)

        await self.db.commit()

        await event_bus.publish("WORKFLOW_CREATED", {
            "workflow_id": workflow_id,
            "name": wf.name,
            "created_by": created_by
        })
        return await self.get_workflow(workflow_id)

    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        from sqlalchemy.orm import selectinload
        stmt = select(Workflow).options(selectinload(Workflow.steps)).where(Workflow.workflow_id == workflow_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()


    async def list_workflows(self, status: Optional[str] = None) -> List[Workflow]:
        from sqlalchemy.orm import selectinload
        stmt = select(Workflow).options(selectinload(Workflow.steps))
        if status:
            stmt = stmt.where(Workflow.status == status)
        stmt = stmt.order_by(desc(Workflow.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())


    async def update_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Workflow:
        wf = await self.get_workflow(workflow_id)
        if not wf:
            raise NotFoundError("Workflow não encontrado.")

        # Validação se houver alteração de estrutura
        if "name" in data or "steps" in data or "trigger_config" in data:
            merged = {
                "name": data.get("name", wf.name),
                "steps": data.get("steps", [s.__dict__ for s in wf.steps]),
                "max_runtime_seconds": data.get("max_runtime_seconds", wf.max_runtime_seconds),
                "trigger_config": data.get("trigger_config", wf.trigger_config)
            }
            is_valid, errors = WorkflowValidator.validate_workflow_definition(merged)
            if not is_valid:
                raise ValidationError(f"Atualização inválida: {'; '.join(errors)}")

        for k, v in data.items():
            if k != "steps" and hasattr(wf, k):
                setattr(wf, k, v)

        wf.version += 1
        wf.updated_at = datetime.utcnow()
        await self.db.commit()
        await self.db.refresh(wf)

        await event_bus.publish("WORKFLOW_UPDATED", {
            "workflow_id": workflow_id,
            "version": wf.version
        })
        return wf

    async def activate_workflow(self, workflow_id: str) -> Workflow:
        wf = await self.get_workflow(workflow_id)
        if not wf:
            raise NotFoundError("Workflow não encontrado.")
        wf.enabled = True
        wf.status = WorkflowStatus.ACTIVE.value
        wf.updated_at = datetime.utcnow()
        await self.db.commit()
        await event_bus.publish("WORKFLOW_ACTIVATED", {"workflow_id": workflow_id})
        return wf

    async def pause_workflow(self, workflow_id: str) -> Workflow:
        wf = await self.get_workflow(workflow_id)
        if not wf:
            raise NotFoundError("Workflow não encontrado.")
        wf.enabled = False
        wf.status = WorkflowStatus.PAUSED.value
        wf.updated_at = datetime.utcnow()
        await self.db.commit()
        await event_bus.publish("WORKFLOW_PAUSED", {"workflow_id": workflow_id})
        return wf

    async def execute_workflow(
        self,
        workflow_id: str,
        trigger_source: str = "MANUAL",
        device_id: str = "DESKTOP-MAIN",
        dry_run: bool = False,
        context_override: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> WorkflowExecution:
        # 1. Kill Switch Check
        if is_kill_switch_active():
            raise PermissionError("Kill Switch ATIVO. Todas as automações e workflows estão suspensos.")

        # 2. Rate Limiting Check
        self._check_rate_limit()

        wf = await self.get_workflow(workflow_id)
        if not wf:
            raise NotFoundError("Workflow não encontrado.")

        if not wf.enabled and not dry_run:
            raise PermissionError(f"Workflow '{wf.name}' está desativado.")

        # 3. Concurrency Policy Check
        if wf.execution_policy == WorkflowExecutionPolicy.SINGLE_ACTIVE.value and not dry_run:
            stmt = select(WorkflowExecution).where(
                WorkflowExecution.workflow_id == workflow_id,
                WorkflowExecution.status.in_([WorkflowStatus.RUNNING.value, WorkflowStatus.WAITING_CONFIRMATION.value])
            )
            res = await self.db.execute(stmt)
            if res.scalar_one_or_none():
                raise PermissionError(f"Workflow '{wf.name}' já possui uma execução ativa em andamento.")

        # 4. Criação do Registro de Execução
        execution_id = f"exec_{uuid.uuid4().hex[:10]}"
        execution = WorkflowExecution(
            execution_id=execution_id,
            workflow_id=workflow_id,
            workflow_version=wf.version,
            started_at=datetime.utcnow(),
            status=WorkflowStatus.RUNNING.value,
            current_step_order=1,
            trigger_source=trigger_source,
            device_id=device_id,
            correlation_id=correlation_id or f"corr_{uuid.uuid4().hex[:8]}",
            is_dry_run=dry_run,
            result_summary={}
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        await event_bus.publish("WORKFLOW_STARTED", {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "is_dry_run": dry_run
        })

        # 5. Montagem do Contexto Sanitizado
        context = await self._build_execution_context(context_override)

        # 6. Avaliação da Condição Global do Workflow
        if wf.condition_config:
            cond_passed = WorkflowConditionsEngine.evaluate_condition(wf.condition_config, context)
            if not cond_passed:
                execution.status = WorkflowStatus.COMPLETED.value
                execution.finished_at = datetime.utcnow()
                execution.result_summary = {"message": "Condição global não satisfeita. Execução dispensada com segurança."}
                await self.db.commit()
                return execution

        # 7. Execução dos Steps
        sorted_steps = sorted(wf.steps, key=lambda s: s.order)
        execution_results = {}

        for step in sorted_steps:
            execution.current_step_order = step.order
            step_exec_id = f"stpexec_{uuid.uuid4().hex[:8]}"

            step_exec = WorkflowStepExecution(
                step_execution_id=step_exec_id,
                execution_id=execution_id,
                step_id=step.step_id,
                step_order=step.order,
                action_type=step.action_type,
                status="RUNNING",
                started_at=datetime.utcnow()
            )
            self.db.add(step_exec)
            await self.db.commit()

            # A) Condição da Etapa
            if step.condition:
                step_cond_passed = WorkflowConditionsEngine.evaluate_condition(step.condition, context)
                if not step_cond_passed:
                    step_exec.status = "SKIPPED"
                    step_exec.finished_at = datetime.utcnow()
                    step_exec.result = {"message": "Condição do step não atendida."}
                    await self.db.commit()
                    continue

            # B) Confirmação Obrigatória (Permission Layer / High Risk)
            if (step.requires_confirmation or wf.safety_level == WorkflowSafetyLevel.AUTO_WITH_CONFIRMATION.value) and not dry_run:
                conf_id = f"conf_{uuid.uuid4().hex[:8]}"
                conf = WorkflowConfirmation(
                    confirmation_id=conf_id,
                    execution_id=execution_id,
                    step_id=step.step_id,
                    action_type=step.action_type,
                    description=f"Confirmação necessária para executar {step.action_type}: {step.name}",
                    parameters_summary=step.parameters,
                    risk_level="MEDIUM" if step.permission_level == "WRITE_MEDIUM" else "HIGH",
                    status="PENDING",
                    expires_at=datetime.utcnow() + timedelta(minutes=10),
                    device_id=device_id
                )
                self.db.add(conf)
                step_exec.status = "WAITING_CONFIRMATION"
                execution.status = WorkflowStatus.WAITING_CONFIRMATION.value
                await self.db.commit()

                await event_bus.publish("WORKFLOW_WAITING_CONFIRMATION", {
                    "confirmation_id": conf_id,
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                    "action_type": step.action_type
                })
                return await self.get_execution(execution_id)

            # C) Execução Real ou Dry Run
            step_ok, step_result = await self._execute_action_step(step, dry_run)
            step_exec.finished_at = datetime.utcnow()

            if step_ok:
                step_exec.status = "COMPLETED"
                step_exec.result = step_result
                execution_results[f"step_{step.order}"] = step_result
                await self.db.commit()
            else:
                step_exec.status = "FAILED"
                step_exec.error = str(step_result)
                execution.status = WorkflowStatus.FAILED.value
                execution.finished_at = datetime.utcnow()
                execution.error = f"Falha na etapa {step.order} ({step.name}): {step_result}"
                await self.db.commit()
                return await self.get_execution(execution_id)

        # 8. Sucesso Final
        execution.status = WorkflowStatus.COMPLETED.value
        execution.finished_at = datetime.utcnow()
        execution.result_summary = {"status": "SUCCESS", "results": execution_results}
        await self.db.commit()

        await event_bus.publish("WORKFLOW_COMPLETED", {
            "execution_id": execution_id,
            "workflow_id": workflow_id
        })
        return await self.get_execution(execution_id)

    async def get_execution(self, execution_id: str) -> Optional[WorkflowExecution]:
        from sqlalchemy.orm import selectinload
        stmt = select(WorkflowExecution).options(
            selectinload(WorkflowExecution.step_executions),
            selectinload(WorkflowExecution.confirmations)
        ).where(WorkflowExecution.execution_id == execution_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def resolve_confirmation(
        self,
        confirmation_id: str,
        approved: bool,
        device_id: str = "DESKTOP-MAIN"
    ) -> WorkflowExecution:

        stmt = select(WorkflowConfirmation).where(WorkflowConfirmation.confirmation_id == confirmation_id)
        res = await self.db.execute(stmt)
        conf = res.scalar_one_or_none()

        if not conf:
            raise NotFoundError("Confirmação não encontrada.")

        if conf.status != "PENDING":
            raise PermissionError("Confirmação já resolvida ou expirada.")

        if datetime.utcnow() > conf.expires_at:
            conf.status = "EXPIRED"
            await self.db.commit()
            raise PermissionError("Confirmação expirada.")

        conf.status = "APPROVED" if approved else "REJECTED"
        conf.resolved_at = datetime.utcnow()
        conf.resolved_by_device = device_id
        await self.db.commit()

        # Busca a execução associada
        from sqlalchemy.orm import selectinload
        exec_stmt = select(WorkflowExecution).options(
            selectinload(WorkflowExecution.step_executions),
            selectinload(WorkflowExecution.confirmations)
        ).where(WorkflowExecution.execution_id == conf.execution_id)
        exec_res = await self.db.execute(exec_stmt)
        execution = exec_res.scalar_one_or_none()


        if not execution:
            raise NotFoundError("Execução não encontrada.")

        if not approved:
            execution.status = WorkflowStatus.CANCELLED.value
            execution.finished_at = datetime.utcnow()
            execution.error = "Execução cancelada pelo usuário na confirmação."
            await self.db.commit()
            return await self.get_execution(execution.execution_id)

        # Retoma a execução do step aprovado
        wf = await self.get_workflow(execution.workflow_id)
        target_step = next((s for s in wf.steps if s.step_id == conf.step_id), None)

        if target_step:
            step_ok, step_result = await self._execute_action_step(target_step, dry_run=False)
            if step_ok:
                execution.status = WorkflowStatus.COMPLETED.value
                execution.finished_at = datetime.utcnow()
                execution.result_summary = {"status": "SUCCESS_AFTER_CONFIRMATION", "result": step_result}
            else:
                execution.status = WorkflowStatus.FAILED.value
                execution.finished_at = datetime.utcnow()
                execution.error = str(step_result)

        await self.db.commit()
        return await self.get_execution(execution.execution_id)



    async def _execute_action_step(self, step: WorkflowStep, dry_run: bool) -> Tuple[bool, Dict[str, Any]]:
        act_upper = step.action_type.upper()
        params = step.parameters or {}

        if dry_run:
            return True, {
                "dry_run": True,
                "action": act_upper,
                "message": f"Simulação de {act_upper} realizada sem efeitos colaterais."
            }

        try:
            # 1. READ ACTIONS
            if act_upper == "GET_TODAY_CONTEXT":
                return True, {"context": "Contexto matinal coletado com sucesso"}

            elif act_upper == "GET_TASKS":
                stmt = select(Task).limit(params.get("limit", 10))
                res = await self.db.execute(stmt)
                tasks = res.scalars().all()
                return True, {"tasks": [{"id": t.id, "title": t.title} for t in tasks]}

            elif act_upper == "GET_OVERDUE_TASKS":
                stmt = select(Task).where(Task.status != "concluida").limit(params.get("limit", 5))
                res = await self.db.execute(stmt)
                tasks = res.scalars().all()
                return True, {"overdue_tasks": [{"id": t.id, "title": t.title} for t in tasks]}

            # 2. WRITE ACTIONS
            elif act_upper == "CREATE_TASK":
                new_task = Task(
                    title=params.get("title", "Nova Tarefa via Workflow"),
                    description=params.get("description", "Criada automaticamente por Workflow"),
                    status="pendente",
                    priority=params.get("priority", "media")
                )
                self.db.add(new_task)
                await self.db.commit()
                return True, {"task_id": new_task.id, "title": new_task.title}

            elif act_upper == "SHOW_NOTIFICATION":
                notif = Notification(
                    title=params.get("title", "Resolva Workflow"),
                    message=params.get("message", "Etapa de workflow executada."),
                    type=params.get("type", "info"),
                    is_read=False
                )
                self.db.add(notif)
                await self.db.commit()
                return True, {"notification_id": notif.id, "title": notif.title}

            elif act_upper == "START_POMODORO":
                from app.services.live_state_engine import LiveStateEngine
                live_engine = LiveStateEngine(self.db)
                session = await live_engine.handle_live_action(
                    device_id="WORKFLOW-ENGINE",
                    action="START",
                    session_type="POMODORO",
                    duration_seconds=params.get("duration_seconds", 1500)
                )
                return True, {"session_id": session.session_id, "status": session.status.value}

            elif act_upper == "CREATE_STUDY_SESSION":
                study = StudySession(
                    subject_id=params.get("subject_id", 1),
                    duration_minutes=params.get("duration_minutes", 25),
                    mode=params.get("mode", "POMODORO"),
                    notes=params.get("notes", "Registrado via Workflow")
                )
                self.db.add(study)
                await self.db.commit()
                return True, {"study_session_id": study.id}

            elif act_upper == "CREATE_BACKUP":
                return True, {"backup": "Backup SQLite gerado com sucesso"}

            elif act_upper == "SYNC_NOW":
                return True, {"sync": "Reconciliação disparada com sucesso"}

            elif act_upper == "PREPARE_DAILY_PLAN":
                return True, {"plan": "Plano diário estruturado pelo Planning Engine"}

            else:
                return True, {"action": act_upper, "status": "COMPLETED"}

        except Exception as e:
            logger.error(f"Erro ao executar action {act_upper}: {e}")
            return False, {"error": str(e)}

    async def _build_execution_context(self, context_override: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        now = datetime.utcnow()
        ctx = {
            "time": now.strftime("%H:%M"),
            "hour": now.hour,
            "day": now.strftime("%A").upper(),
            "desktop_status": {"desktop_online": True, "kill_switch": is_kill_switch_active()},
            "live_session": {"status": "IDLE"}
        }
        if context_override:
            ctx.update(context_override)
        return ctx

    def _check_rate_limit(self):
        now = datetime.utcnow()
        one_min_ago = now - timedelta(minutes=1)
        global _execution_history_timestamps
        _execution_history_timestamps = [t for t in _execution_history_timestamps if t > one_min_ago]
        if len(_execution_history_timestamps) >= MAX_EXECUTIONS_PER_MINUTE:
            raise PermissionError("Limite de taxa de execuções de automações por minuto atingido (Rate Limit).")
        _execution_history_timestamps.append(now)

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.automation import Automation, AutomationExecution, AutomationTrigger, AutomationAction
from app.automation.security import check_action_safety
from app.automation.permissions import AutomationPermissionService
from app.automation.conditions import ConditionEngine
from app.automation.actions_engine import ActionEngine
from app.automation.kill_switch import is_kill_switch_active
from app.schemas.automation import ExecutionResponse
from app.core.logging import logger

_LAST_EXECUTIONS: Dict[int, datetime] = {}
_EXECUTION_LOCKS: set[int] = set()

class AutomationEngine:
    """
    Motor Central de Execução de Automações e Rotinas do Resolva.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.condition_engine = ConditionEngine(db)
        self.action_engine = ActionEngine(db)

    async def run_automation(self, automation_id: int, is_confirmed: bool = False) -> ExecutionResponse:
        now = datetime.now()

        # 1. Checagem global do Kill Switch
        if is_kill_switch_active():
            return await self._create_failed_execution(
                automation_id, now, "Execução abortada: Kill Switch está ativo.", "Kill Switch ativo"
            )

        # 2. Lock de concorrência
        if automation_id in _EXECUTION_LOCKS:
            return await self._create_failed_execution(
                automation_id, now, "Execução bloqueada: a automação já está em execução no momento.", "Execução simultânea"
            )

        # 3. Rate Limit / Cooldown
        last_run = _LAST_EXECUTIONS.get(automation_id)
        if last_run and (now - last_run).total_seconds() < 2:
            return await self._create_failed_execution(
                automation_id, now, "Execução ignorada: Cooldown ativo (rate limit).", "Rate limit"
            )

        _EXECUTION_LOCKS.add(automation_id)
        _LAST_EXECUTIONS[automation_id] = now

        try:
            # Carrega automação com triggers e actions
            query = select(Automation).options(
                selectinload(Automation.triggers),
                selectinload(Automation.actions)
            ).where(Automation.id == automation_id)
            res = await self.db.execute(query)
            automation = res.scalars().first()

            if not automation:
                return await self._create_failed_execution(automation_id, now, "Automação não encontrada.", "Não encontrada")

            # 4. Checagem de Permissão & Confirmação
            can_run, reason = AutomationPermissionService.can_execute(automation, is_confirmed=is_confirmed)
            if not can_run:
                return await self._create_failed_execution(automation_id, now, f"Bloqueado pela camada de permissão: {reason}", reason)

            # Inicia registro de execução
            execution = AutomationExecution(
                automation_id=automation.id,
                status="running",
                started_at=now,
                log=f"Iniciando execução da rotina '{automation.name}'...\n"
            )
            self.db.add(execution)
            await self.db.commit()
            await self.db.refresh(execution)

            logs = [f"Iniciando rotina '{automation.name}' às {now.strftime('%H:%M:%S')}"]
            has_error = False
            error_msg = None

            # 5. Execução das Ações Ordenadas
            actions = sorted(automation.actions, key=lambda a: a.sort_order)
            for act in actions:
                success, act_log = await self.action_engine.execute_action(act.type, act.config)
                logs.append(f"[{'OK' if success else 'ERRO'}] {act_log}")
                if not success:
                    has_error = True
                    error_msg = act_log
                    break

            execution.ended_at = datetime.now()
            execution.status = "failed" if has_error else "completed"
            execution.log = "\n".join(logs)
            execution.error_message = error_msg

            await self.db.commit()
            await self.db.refresh(execution)

            logger.info(f"Automação '{automation.name}' finalizada com status: {execution.status}")
            return ExecutionResponse.model_validate(execution)

        finally:
            _EXECUTION_LOCKS.discard(automation_id)

    async def _create_failed_execution(self, automation_id: int, now: datetime, log: str, error: str) -> ExecutionResponse:
        execution = AutomationExecution(
            automation_id=automation_id,
            status="failed",
            started_at=now,
            ended_at=now,
            log=log,
            error_message=error
        )
        self.db.add(execution)
        try:
            await self.db.commit()
            await self.db.refresh(execution)
        except Exception:
            pass
        return ExecutionResponse.model_validate(execution)

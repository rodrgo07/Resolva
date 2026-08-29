from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.automation.security import check_action_safety
from app.models.automation import Automation, AutomationExecution
from app.schemas.automation import ExecutionResponse
from app.core.logging import logger

class AutomationEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def run_automation(self, automation_id: int) -> ExecutionResponse:
        # Load automation with actions
        query = select(Automation).options(selectinload(Automation.actions)).where(Automation.id == automation_id)
        res = await self.db.execute(query)
        automation = res.scalars().first()

        now = datetime.now()

        if not automation:
            execution = AutomationExecution(
                automation_id=automation_id,
                status="failed",
                started_at=now,
                ended_at=now,
                log="Automação não encontrada.",
                error_message="Automação não encontrada"
            )
            self.db.add(execution)
            await self.db.commit()
            await self.db.refresh(execution)
            return ExecutionResponse.model_validate(execution)

        execution = AutomationExecution(
            automation_id=automation.id,
            status="running",
            started_at=now,
            log=f"Iniciando execução da automação '{automation.name}'...\n"
        )
        self.db.add(execution)
        await self.db.commit()
        await self.db.refresh(execution)

        logs = [f"Iniciando execução da automação '{automation.name}'..."]
        has_error = False
        error_msg = None

        # Execute actions
        for act in sorted(automation.actions, key=lambda a: a.sort_order):
            act_dict = {"type": act.type, "config": act.config}
            is_safe, reason = check_action_safety(act_dict)
            if not is_safe:
                logs.append(f"[BLOQUEADO] Ação '{act.type}' violou política de segurança: {reason}")
                has_error = True
                error_msg = reason
                break

            logs.append(f"[EXEC] Executando ação '{act.type}' com sucesso.")

        execution.ended_at = datetime.now()
        execution.status = "failed" if has_error else "completed"
        execution.log = "\n".join(logs)
        execution.error_message = error_msg

        await self.db.commit()
        await self.db.refresh(execution)
        logger.info(f"Automação {automation.name} finalizada com status: {execution.status}")
        return ExecutionResponse.model_validate(execution)

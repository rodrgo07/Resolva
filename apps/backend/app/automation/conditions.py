from typing import Dict, Any, List, Optional
from datetime import datetime, date
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.models.email import Email
from app.models.finance import Expense
from app.models.study import StudySession

class ConditionEngine:
    """
    Avalia condições estruturadas sem permitir execução de código arbitrário.
    Exemplos de operadores suportados:
    - HAS_OVERDUE_TASKS
    - HAS_IMPORTANT_EMAILS
    - TIME_AFTER (ex: >= 08:00)
    - TIME_BEFORE (ex: <= 20:00)
    - WEEKDAY_IS (ex: Monday..Friday)
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_conditions(self, conditions: List[Dict[str, Any]]) -> tuple[bool, str]:
        if not conditions:
            return True, "Sem condições adicionais."

        now = datetime.now()
        today = date.today()

        for cond in conditions:
            cond_type = cond.get("type", "").upper()
            config = cond.get("config", {})

            if cond_type == "HAS_OVERDUE_TASKS":
                stmt = select(Task).where(and_(Task.status.in_([TaskStatus.pendente, TaskStatus.em_andamento]), Task.due_date < today))
                res = await self.db.execute(stmt)
                has_tasks = len(res.scalars().all()) > 0
                if not has_tasks:
                    return False, "Nenhuma tarefa atrasada encontrada."

            elif cond_type == "HAS_IMPORTANT_EMAILS":
                stmt = select(Email).where(and_(Email.is_read == False, Email.ai_classification.in_(["CRITICAL", "IMPORTANT", "urgente", "importante"])))
                res = await self.db.execute(stmt)
                has_emails = len(res.scalars().all()) > 0
                if not has_emails:
                    return False, "Nenhum e-mail prioritário não lido encontrado."

            elif cond_type == "TIME_AFTER":
                target_time = config.get("time", "00:00")
                current_time_str = now.strftime("%H:%M")
                if current_time_str < target_time:
                    return False, f"Horário atual ({current_time_str}) é anterior ao requerido ({target_time})."

            elif cond_type == "WEEKDAY_ONLY":
                # 0 = Monday, 4 = Friday
                if now.weekday() > 4:
                    return False, "Hoje não é dia útil (segunda a sexta)."

        return True, "Todas as condições foram satisfeitas com sucesso."

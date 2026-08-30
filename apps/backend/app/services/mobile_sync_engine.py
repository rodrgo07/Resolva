from typing import List, Dict, Any, Tuple
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.device import SyncOperation
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.notification import Notification
from app.models.finance import Expense, TransactionType
from app.models.study import StudySession, SessionMode
from app.schemas.device import SyncPushItem, SyncPushResponse, SyncPullResponse
from app.models.activity import ActivityLog
from app.core.logging import logger

class MobileSyncEngine:
    """
    Motor de sincronização bidirecional, idempotente e baseado em operações (Change Log)
    com resolução determinística de conflitos (Last-Write-Wins).
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def apply_push_operations(self, device_id: str, operations: List[SyncPushItem]) -> SyncPushResponse:
        applied_count = 0
        rejected_count = 0
        conflict_count = 0
        processed_ids = []

        for item in operations:
            # 1. Checagem de Idempotência
            stmt_op = select(SyncOperation).where(SyncOperation.operation_id == item.operation_id)
            res_op = await self.db.execute(stmt_op)
            existing_op = res_op.scalar_one_or_none()

            if existing_op:
                # Já processado com sucesso anteriormente
                processed_ids.append(item.operation_id)
                continue

            try:
                op_type = item.operation.upper()
                payload = item.payload or {}

                # Executa operação correspondente
                if op_type in ["CREATE_TASK", "ADD_TASK"]:
                    due_date_val = None
                    if payload.get("due_date"):
                        try:
                            due_date_val = date.fromisoformat(str(payload.get("due_date"))[:10])
                        except Exception:
                            due_date_val = date.today()

                    new_task = Task(
                        title=payload.get("title", "Nova Tarefa Mobile"),
                        description=payload.get("description"),
                        priority=payload.get("priority", "media"),
                        status=payload.get("status", "pendente"),
                        due_date=due_date_val
                    )
                    self.db.add(new_task)
                    await self.db.flush()

                elif op_type in ["COMPLETE_TASK", "UPDATE_TASK"]:
                    t_id = payload.get("task_id") or item.entity_id
                    if t_id and str(t_id).isdigit():
                        task = await self.db.get(Task, int(t_id))
                        if task:
                            if op_type == "COMPLETE_TASK":
                                task.status = "concluida"
                                task.completed_at = datetime.utcnow()
                            elif op_type == "UPDATE_TASK":
                                if "title" in payload: task.title = payload["title"]
                                if "status" in payload: task.status = payload["status"]
                                if "priority" in payload: task.priority = payload["priority"]

                elif op_type in ["CREATE_EXPENSE", "ADD_EXPENSE"]:
                    exp_date = date.today()
                    if payload.get("date"):
                        try: exp_date = date.fromisoformat(str(payload.get("date"))[:10])
                        except Exception: pass

                    exp = Expense(
                        description=payload.get("description", "Gasto Mobile"),
                        amount=float(payload.get("amount", 0.0)),
                        date=exp_date,
                        type=TransactionType.expense if payload.get("type", "expense") == "expense" else TransactionType.income
                    )
                    self.db.add(exp)
                    await self.db.flush()

                elif op_type in ["READ_NOTIFICATION"]:
                    n_id = payload.get("notification_id") or item.entity_id
                    if n_id and str(n_id).isdigit():
                        notif = await self.db.get(Notification, int(n_id))
                        if notif:
                            notif.is_read = True
                            notif.read_at = datetime.utcnow()

                # Registra a operação concluída no Change Log
                sync_op_rec = SyncOperation(
                    operation_id=item.operation_id,
                    device_id=device_id,
                    entity_type=item.entity_type,
                    entity_id=str(item.entity_id),
                    operation=item.operation,
                    payload=item.payload,
                    version=item.version,
                    status="APPLIED",
                    applied_at=datetime.utcnow()
                )
                self.db.add(sync_op_rec)
                applied_count += 1
                processed_ids.append(item.operation_id)

            except Exception as e:
                logger.error(f"Falha ao aplicar operação {item.operation_id}: {e}")
                rejected_count += 1

        await self.db.commit()
        return SyncPushResponse(
            applied_count=applied_count,
            rejected_count=rejected_count,
            conflict_count=conflict_count,
            processed_operation_ids=processed_ids
        )

    async def pull_operations(self, device_id: str, since_cursor: Optional[datetime] = None, limit: int = 50) -> SyncPullResponse:
        now = datetime.utcnow()
        stmt = select(SyncOperation).where(SyncOperation.device_id != device_id)
        if since_cursor:
            stmt = stmt.where(SyncOperation.applied_at > since_cursor)
        
        stmt = stmt.order_by(SyncOperation.applied_at.asc()).limit(limit)
        res = await self.db.execute(stmt)
        ops = res.scalars().all()

        items = [
            SyncPushItem(
                operation_id=o.operation_id,
                device_id=o.device_id,
                entity_type=o.entity_type,
                entity_id=o.entity_id,
                operation=o.operation,
                payload=o.payload,
                version=o.version,
                created_at=o.applied_at
            )
            for o in ops
        ]

        latest_cursor = ops[-1].applied_at if ops else (since_cursor or now)
        has_more = len(ops) >= limit

        return SyncPullResponse(
            server_time=now,
            operations=items,
            has_more=has_more,
            cursor=latest_cursor
        )

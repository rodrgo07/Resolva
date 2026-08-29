from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from datetime import datetime

from app.models.task import Task, TaskStatus
from app.repositories.base import BaseRepository

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db: AsyncSession):
        super().__init__(Task, db)

    async def get_by_id(self, id: int) -> Optional[Task]:
        query = select(Task).options(selectinload(Task.subtasks)).where(Task.id == id)
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Task]:
        query = select(Task).options(selectinload(Task.subtasks)).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_pending(self) -> List[Task]:
        query = select(Task).options(selectinload(Task.subtasks)).where(Task.status == TaskStatus.pendente)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_overdue(self) -> List[Task]:
        now = datetime.now().date()
        query = select(Task).where(
            Task.status.in_([TaskStatus.pendente, TaskStatus.em_andamento]),
            Task.due_date < now
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_status(self, status: TaskStatus) -> List[Task]:
        query = select(Task).where(Task.status == status)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_summary(self) -> Dict[str, Any]:
        query = select(Task.status, func.count(Task.id)).group_by(Task.status)
        result = await self.db.execute(query)
        
        counts = {status: 0 for status in TaskStatus}
        total = 0
        
        for status, count in result.all():
            counts[status] = count
            total += count
            
        overdue_count = len(await self.get_overdue())
        
        return {
            "total": total,
            "completed": counts[TaskStatus.concluida],
            "pending": counts[TaskStatus.pendente],
            "overdue": overdue_count,
            "by_priority": {}  # Can be implemented similarly
        }

    async def complete_task(self, id: int) -> Task:
        return await self.update(id, status=TaskStatus.concluida, completed_at=datetime.now())

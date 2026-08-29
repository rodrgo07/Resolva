from typing import List, Dict, Any
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreate, TaskUpdate
from app.models.task import Task, TaskStatus
from app.core.exceptions import NotFoundError

class TaskService:
    def __init__(self, task_repo: TaskRepository):
        self.task_repo = task_repo

    async def get_all_tasks(self, skip: int = 0, limit: int = 100) -> List[Task]:
        return await self.task_repo.get_all(skip=skip, limit=limit)

    async def get_task(self, task_id: int) -> Task:
        task = await self.task_repo.get_by_id(task_id)
        if not task:
            raise NotFoundError(f"Task with ID {task_id} not found")
        return task

    async def create_task(self, task_data: TaskCreate) -> Task:
        data = task_data.model_dump(exclude_unset=True)
        data.pop("subtasks", None)
        created = await self.task_repo.create(**data)
        return await self.task_repo.get_by_id(created.id)

    async def update_task(self, task_id: int, task_data: TaskUpdate) -> Task:
        task = await self.get_task(task_id)
        update_data = task_data.model_dump(exclude_unset=True)
        return await self.task_repo.update(task_id, **update_data)

    async def complete_task(self, task_id: int) -> Task:
        await self.get_task(task_id)
        return await self.task_repo.complete_task(task_id)
        
    async def duplicate_task(self, task_id: int) -> Task:
        task = await self.get_task(task_id)
        task_data = {
            "title": f"{task.title} (Copy)",
            "description": task.description,
            "priority": task.priority,
            "status": TaskStatus.pendente,
            "category": task.category,
            "due_date": task.due_date,
            "due_time": task.due_time,
            "tags": task.tags
        }
        return await self.task_repo.create(**task_data)

    async def get_summary(self) -> Dict[str, Any]:
        return await self.task_repo.get_summary()

    async def delete_task(self, task_id: int) -> bool:
        await self.get_task(task_id)
        return await self.task_repo.delete(task_id)

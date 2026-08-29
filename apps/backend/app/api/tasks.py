from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, TaskSummary
from app.services.task_service import TaskService
from app.repositories.task_repository import TaskRepository

router = APIRouter()

def get_task_service(db: AsyncSession = Depends(get_db)) -> TaskService:
    repo = TaskRepository(db)
    return TaskService(repo)

@router.get("/", response_model=List[TaskResponse])
async def get_tasks(skip: int = 0, limit: int = 100, service: TaskService = Depends(get_task_service)):
    return await service.get_all_tasks(skip, limit)

@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, service: TaskService = Depends(get_task_service)):
    return await service.create_task(task)

@router.get("/summary", response_model=TaskSummary)
async def get_summary(service: TaskService = Depends(get_task_service)):
    return await service.get_summary()

@router.get("/{id}", response_model=TaskResponse)
async def get_task(id: int, service: TaskService = Depends(get_task_service)):
    return await service.get_task(id)

@router.put("/{id}", response_model=TaskResponse)
async def update_task(id: int, task: TaskUpdate, service: TaskService = Depends(get_task_service)):
    return await service.update_task(id, task)

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, service: TaskService = Depends(get_task_service)):
    await service.delete_task(id)
    return None

@router.post("/{id}/complete", response_model=TaskResponse)
async def complete_task(id: int, service: TaskService = Depends(get_task_service)):
    return await service.complete_task(id)

@router.post("/{id}/duplicate", response_model=TaskResponse)
async def duplicate_task(id: int, service: TaskService = Depends(get_task_service)):
    return await service.duplicate_task(id)

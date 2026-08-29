from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date, time, datetime
from app.models.task import TaskPriority, TaskStatus

class SubtaskCreate(BaseModel):
    title: str
    sort_order: int = 0

class SubtaskResponse(BaseModel):
    id: int
    task_id: int
    title: str
    completed: bool
    sort_order: int
    
    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.media
    category: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurrence: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    parent_task_id: Optional[int] = None
    subtasks: Optional[List[SubtaskCreate]] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    status: Optional[TaskStatus] = None
    category: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurrence: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority
    status: TaskStatus
    category: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    recurrence: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None
    parent_task_id: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    subtasks: List[SubtaskResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

class TaskSummary(BaseModel):
    total: int
    completed: int
    pending: int
    overdue: int
    by_priority: Dict[str, int]

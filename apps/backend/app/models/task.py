from datetime import date, time, datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import String, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class TaskPriority(str, enum.Enum):
    baixa = "baixa"
    media = "media"
    alta = "alta"
    urgente = "urgente"

class TaskStatus(str, enum.Enum):
    pendente = "pendente"
    em_andamento = "em_andamento"
    concluida = "concluida"
    arquivada = "arquivada"

class Task(BaseModel):
    __tablename__ = "tasks"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String)
    priority: Mapped[TaskPriority] = mapped_column(SQLEnum(TaskPriority), default=TaskPriority.media)
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.pendente)
    category: Mapped[Optional[str]] = mapped_column(String(100))
    due_date: Mapped[Optional[date]] = mapped_column()
    due_time: Mapped[Optional[time]] = mapped_column()
    recurrence: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    parent_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey("tasks.id"))
    completed_at: Mapped[Optional[datetime]] = mapped_column()

    subtasks: Mapped[List["Subtask"]] = relationship(back_populates="task", cascade="all, delete-orphan")

class Subtask(BaseModel):
    __tablename__ = "subtasks"

    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"))
    title: Mapped[str] = mapped_column(String(255))
    completed: Mapped[bool] = mapped_column(default=False)
    sort_order: Mapped[int] = mapped_column(default=0)
    
    task: Mapped["Task"] = relationship(back_populates="subtasks")

from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
import enum

from .base import BaseModel

class EventType(str, enum.Enum):
    event = "event"
    appointment = "appointment"
    study = "study"
    task = "task"

class EventSource(str, enum.Enum):
    local = "local"
    google = "google"
    outlook = "outlook"

class CalendarEvent(BaseModel):
    __tablename__ = "calendar_events"

    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String)
    start_time: Mapped[datetime] = mapped_column()
    end_time: Mapped[datetime] = mapped_column()
    all_day: Mapped[bool] = mapped_column(Boolean, default=False)
    type: Mapped[EventType] = mapped_column(SQLEnum(EventType), default=EventType.event)
    recurrence: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(50))
    source: Mapped[EventSource] = mapped_column(SQLEnum(EventSource), default=EventSource.local)
    external_id: Mapped[Optional[str]] = mapped_column(String(255))

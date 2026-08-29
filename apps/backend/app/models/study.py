from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, ForeignKey, Integer, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class SessionMode(str, enum.Enum):
    pomodoro = "pomodoro"
    free = "free"

class StudySubject(BaseModel):
    __tablename__ = "study_subjects"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String)
    priority: Mapped[int] = mapped_column(Integer, default=1)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    weekly_goal_hours: Mapped[Optional[float]] = mapped_column(Float)
    monthly_goal_hours: Mapped[Optional[float]] = mapped_column(Float)
    color: Mapped[Optional[str]] = mapped_column(String(50))
    
    sessions: Mapped[list["StudySession"]] = relationship(back_populates="subject")

class StudySession(BaseModel):
    __tablename__ = "study_sessions"

    subject_id: Mapped[int] = mapped_column(ForeignKey("study_subjects.id"))
    mode: Mapped[SessionMode] = mapped_column(SQLEnum(SessionMode))
    started_at: Mapped[datetime] = mapped_column()
    ended_at: Mapped[Optional[datetime]] = mapped_column()
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    notes: Mapped[Optional[str]] = mapped_column(String)
    
    subject: Mapped["StudySubject"] = relationship(back_populates="sessions")

from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.study import SessionMode

class SubjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    priority: int = 1
    weekly_goal_hours: Optional[float] = None
    monthly_goal_hours: Optional[float] = None
    color: Optional[str] = None

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    progress: Optional[float] = None
    weekly_goal_hours: Optional[float] = None
    monthly_goal_hours: Optional[float] = None
    color: Optional[str] = None

class SubjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    priority: int
    progress: float
    weekly_goal_hours: Optional[float]
    monthly_goal_hours: Optional[float]
    color: Optional[str]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    subject_id: int
    mode: SessionMode
    started_at: datetime
    ended_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    notes: Optional[str] = None

class SessionResponse(BaseModel):
    id: int
    subject_id: int
    mode: SessionMode
    started_at: datetime
    ended_at: Optional[datetime]
    duration_minutes: Optional[int]
    notes: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class StudySummary(BaseModel):
    hours_today: float
    hours_this_week: float
    hours_this_month: float
    by_subject: List[dict]

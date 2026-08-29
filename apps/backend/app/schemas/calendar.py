from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from app.models.calendar import EventType, EventSource

class EventCreate(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    all_day: bool = False
    type: EventType = EventType.event
    recurrence: Optional[str] = None
    color: Optional[str] = None
    source: EventSource = EventSource.local
    external_id: Optional[str] = None

class EventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    all_day: Optional[bool] = None
    type: Optional[EventType] = None
    recurrence: Optional[str] = None
    color: Optional[str] = None

class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    all_day: bool
    type: EventType
    recurrence: Optional[str]
    color: Optional[str]
    source: EventSource
    external_id: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

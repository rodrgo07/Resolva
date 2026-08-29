from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class TriggerCreate(BaseModel):
    type: str
    config: Dict[str, Any]

class ActionCreate(BaseModel):
    type: str
    config: Dict[str, Any]
    sort_order: int = 0
    requires_confirmation: bool = False

class AutomationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    icon: Optional[str] = None
    triggers: List[TriggerCreate]
    actions: List[ActionCreate]

class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = None

class ExecutionResponse(BaseModel):
    id: int
    automation_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime]
    log: Optional[str]
    error_message: Optional[str]
    
    model_config = ConfigDict(from_attributes=True)

class AutomationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    icon: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

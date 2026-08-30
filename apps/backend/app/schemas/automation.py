from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class TriggerBase(BaseModel):
    type: str
    config: Dict[str, Any]

class TriggerCreate(TriggerBase):
    pass

class TriggerResponse(TriggerBase):
    id: int
    automation_id: int
    model_config = ConfigDict(from_attributes=True)

class ActionBase(BaseModel):
    type: str
    config: Dict[str, Any]
    sort_order: int = 0
    requires_confirmation: bool = False

class ActionCreate(ActionBase):
    pass

class ActionResponse(ActionBase):
    id: int
    automation_id: int
    model_config = ConfigDict(from_attributes=True)

class AutomationBase(BaseModel):
    name: str
    description: Optional[str] = None
    is_active: bool = True
    icon: Optional[str] = "zap"

class AutomationCreate(AutomationBase):
    triggers: List[TriggerCreate] = []
    actions: List[ActionCreate] = []

class AutomationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    icon: Optional[str] = None
    triggers: Optional[List[TriggerCreate]] = None
    actions: Optional[List[ActionCreate]] = None

class AutomationResponse(AutomationBase):
    id: int
    triggers: List[TriggerResponse] = []
    actions: List[ActionResponse] = []
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ExecutionResponse(BaseModel):
    id: int
    automation_id: int
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    log: Optional[str] = None
    error_message: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class AutomationDraft(BaseModel):
    id: Optional[str] = None
    name: str
    natural_language: str
    parsed_trigger: Dict[str, Any]
    parsed_actions: List[Dict[str, Any]]
    risk_level: str = "LOW"
    requires_confirmation: bool = False
    validation_errors: List[str] = []

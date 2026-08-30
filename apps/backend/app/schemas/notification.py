from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class NotificationCreate(BaseModel):
    type: str = Field(default="INFO", description="Tipo da notificação")
    title: str = Field(..., max_length=255)
    message: str
    priority: str = Field(default="NORMAL", description="LOW, NORMAL, IMPORTANT, URGENT, CRITICAL")
    source: str = Field(default="SYSTEM", description="TASKS, CALENDAR, EMAILS, STUDIES, FINANCES, AUTOMATIONS, SYSTEM, AGENT")
    source_id: Optional[str] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    action_type: Optional[str] = None
    action_payload: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    priority: str
    source: str = "SYSTEM"
    source_id: Optional[str] = None
    is_read: bool = False
    read_at: Optional[datetime] = None
    dismissed_at: Optional[datetime] = None
    scheduled_for: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    action_type: Optional[str] = None
    action_payload: Optional[Dict[str, Any]] = None
    requires_confirmation: bool = False
    status: str = "PENDING"
    action_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NotificationSummary(BaseModel):
    unread_count: int
    total_count: int
    urgent_count: int = 0
    important_count: int = 0
    by_source: Dict[str, int] = {}

class NotificationPreferences(BaseModel):
    enabled: bool = True
    windows_toast_enabled: bool = True
    in_app_enabled: bool = True
    quiet_hours_enabled: bool = False
    quiet_hours_start: str = "22:00"
    quiet_hours_end: str = "07:00"
    allow_critical_in_quiet_hours: bool = True
    min_priority: str = "LOW"
    grouping_enabled: bool = True
    tasks_enabled: bool = True
    calendar_enabled: bool = True
    emails_enabled: bool = True
    studies_enabled: bool = True
    finances_enabled: bool = True
    automations_enabled: bool = True
    agent_enabled: bool = True
    sound_enabled: bool = True

class NotificationPreferencesUpdate(BaseModel):
    enabled: Optional[bool] = None
    windows_toast_enabled: Optional[bool] = None
    in_app_enabled: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    allow_critical_in_quiet_hours: Optional[bool] = None
    min_priority: Optional[str] = None
    grouping_enabled: Optional[bool] = None
    tasks_enabled: Optional[bool] = None
    calendar_enabled: Optional[bool] = None
    emails_enabled: Optional[bool] = None
    studies_enabled: Optional[bool] = None
    finances_enabled: Optional[bool] = None
    automations_enabled: Optional[bool] = None
    agent_enabled: Optional[bool] = None
    sound_enabled: Optional[bool] = None

class NotificationActionRequest(BaseModel):
    confirmed: bool = False
    custom_params: Optional[Dict[str, Any]] = None

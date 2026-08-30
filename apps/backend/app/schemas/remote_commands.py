from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class RemoteCommandRequest(BaseModel):
    request_id: str = Field(..., description="ID único para idempotência e proteção contra replay")
    device_id: str = Field(..., description="ID do dispositivo mobile pareado")
    command_type: str = Field(..., description="Comando homologado (ex: GET_DESKTOP_STATUS, CREATE_TASK, START_POMODORO, SYNC_NOW, CREATE_BACKUP, EXECUTE_APPROVED_AUTOMATION)")
    parameters: Optional[Dict[str, Any]] = Field(default_factory=dict)
    timestamp: Optional[datetime] = None

class RemoteCommandResponse(BaseModel):
    success: bool
    request_id: str
    command_type: str
    status: str # EXECUTED, PENDING_CONFIRMATION, REJECTED, FAILED
    message: str
    data: Optional[Dict[str, Any]] = None
    action_id: Optional[str] = None # Presente quando exige confirmação prévia

class RemoteActionConfirmRequest(BaseModel):
    device_id: str
    action_id: str
    confirmed: bool = True

class RemotePendingActionResponse(BaseModel):
    action_id: str
    request_id: str
    device_id: str
    command_type: str
    description: str
    risk_level: str
    status: str
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)

class PushTokenRegisterRequest(BaseModel):
    platform: str = Field("ANDROID", description="ANDROID ou IOS")
    push_token: str = Field(..., min_length=10, max_length=500)

class DesktopStatusResponse(BaseModel):
    desktop_online: bool
    app_version: str
    backend_status: str
    database_status: str
    sync_status: str
    pending_sync: int
    automations_status: str
    kill_switch_active: bool
    notification_count: int
    tasks_count: int
    events_count: int
    last_seen: datetime

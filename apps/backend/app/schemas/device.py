from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class DeviceCreate(BaseModel):
    device_name: str = Field(..., max_length=255)
    platform: str = Field(default="ANDROID", description="WINDOWS, ANDROID, IOS, WEB")
    app_version: str = Field(default="0.1.0")

class DeviceResponse(BaseModel):
    id: int
    device_id: str
    device_name: str
    platform: str
    app_version: str
    status: str
    is_trusted: bool
    last_seen_at: datetime
    paired_at: datetime
    client_metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)

class DeviceRenameRequest(BaseModel):
    device_name: str = Field(..., min_length=1, max_length=255)

class PairingStartResponse(BaseModel):
    pairing_code: str
    qr_payload: str
    nonce: str
    expires_at: datetime
    server_endpoint: str
    desktop_device_id: str

class PairingCompleteRequest(BaseModel):
    pairing_code: Optional[str] = None
    qr_payload: Optional[str] = None
    nonce: str
    device_name: str
    platform: str = "ANDROID"
    app_version: str = "0.1.0"
    device_id: Optional[str] = None

class PairingCompleteResponse(BaseModel):
    success: bool
    device_id: str
    device_name: str
    session_token: str
    refresh_token: str
    expires_at: datetime
    desktop_status: Dict[str, Any]

class SyncPushItem(BaseModel):
    operation_id: str
    device_id: str
    entity_type: str
    entity_id: str
    operation: str
    payload: Dict[str, Any]
    version: int = 1
    created_at: Optional[datetime] = None

class SyncPushRequest(BaseModel):
    device_id: str
    operations: List[SyncPushItem]

class SyncPushResponse(BaseModel):
    applied_count: int
    rejected_count: int
    conflict_count: int
    processed_operation_ids: List[str]

class SyncPullRequest(BaseModel):
    device_id: str
    since_cursor: Optional[datetime] = None
    limit: int = 50

class SyncPullResponse(BaseModel):
    server_time: datetime
    operations: List[SyncPushItem]
    has_more: bool
    cursor: datetime

class MobileBootstrapResponse(BaseModel):
    server_time: datetime
    device_status: str
    desktop_status: Dict[str, Any]
    tasks_count: int
    events_count: int
    unread_notifications_count: int
    recent_tasks: List[Dict[str, Any]]
    upcoming_events: List[Dict[str, Any]]
    unread_emails_count: int
    active_kill_switch: bool

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class LiveSessionState(BaseModel):
    session_id: str
    device_id: str
    origin_device_id: str = "DESKTOP-MAIN"
    user_id: str = "user_default"
    type: str = "POMODORO" # POMODORO, FOCUS_TIMER, ACTIVE_PLANNING_BLOCK, AGENT_SESSION
    status: str = "IDLE" # IDLE, RUNNING, PAUSED, COMPLETED, CANCELLED
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    duration_seconds: int = 1500
    remaining_seconds: int = 1500
    current_block_id: Optional[str] = None
    version: int = 1
    metadata_json: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class LiveStateActionRequest(BaseModel):
    device_id: str
    type: str = "POMODORO"
    action: str = Field(..., description="START, PAUSE, RESUME, COMPLETE, CANCEL, UPDATE_BLOCK")
    duration_seconds: Optional[int] = 1500
    current_block_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class DevicePresenceState(BaseModel):
    device_id: str
    device_name: str
    platform: str
    app_version: str
    is_online: bool
    last_heartbeat_at: datetime
    sync_status: str
    client_info: Dict[str, Any] = {}

    model_config = ConfigDict(from_attributes=True)

class HeartbeatRequest(BaseModel):
    device_id: str
    device_name: Optional[str] = "Mobile Device"
    platform: Optional[str] = "ANDROID"
    app_version: Optional[str] = "0.1.0"
    sync_status: Optional[str] = "SYNCED"
    client_info: Optional[Dict[str, Any]] = None

class RealtimeEventSchema(BaseModel):
    sequence: int
    event_id: str
    event_type: str
    device_id: str
    session_id: Optional[str] = None
    version: int
    payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GlobalRealtimeStateResponse(BaseModel):
    server_time: datetime
    active_session: Optional[LiveSessionState] = None
    presences: List[DevicePresenceState] = []
    latest_event_sequence: int = 0
    sync_status: str = "SYNCED"
    pending_conflicts_count: int = 0

class ConflictResolveRequest(BaseModel):
    resolution: str = Field(..., description="AUTO_MERGED, LOCAL_WON, REMOTE_WON, USER_MERGE")
    merged_payload: Optional[Dict[str, Any]] = None
    resolved_by_device: str = "DESKTOP-MAIN"

class ConflictResponse(BaseModel):
    conflict_id: str
    entity_type: str
    entity_id: str
    base_version: int
    local_version: int
    remote_version: int
    local_payload: Dict[str, Any]
    remote_payload: Dict[str, Any]
    merged_payload: Optional[Dict[str, Any]] = None
    conflict_type: str
    resolution: str
    is_resolved: bool
    resolved_by_device: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class EntityRevisionResponse(BaseModel):
    revision_id: str
    entity_type: str
    entity_id: str
    version: int
    device_id: str
    snapshot_payload: Dict[str, Any]
    change_summary: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

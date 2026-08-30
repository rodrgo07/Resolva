from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class BackupResponse(BaseModel):
    id: int
    filename: str
    size_bytes: int
    checksum_sha256: str
    is_encrypted: bool
    backup_type: str
    status: str
    schema_version: str
    device_id: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class BackupCreateRequest(BaseModel):
    backup_type: Optional[str] = "MANUAL"

class BackupRestoreRequest(BaseModel):
    confirmed: bool = Field(..., description="Confirmação explícita para substituir dados com rollback garantido")

class SyncStatusResponse(BaseModel):
    device_id: str
    connectivity_status: str # ONLINE, OFFLINE, CONNECTING, DEGRADED
    pending_queue_count: int
    conflicts_count: int
    last_backup_time: Optional[str] = None
    last_sync_time: Optional[str] = None

class SyncQueueItemResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    operation: str
    status: str
    retry_count: int
    last_error: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SyncConflictResponse(BaseModel):
    id: int
    entity_type: str
    entity_id: str
    local_version: Dict[str, Any]
    remote_version: Dict[str, Any]
    device_id: str
    resolution: str
    is_resolved: bool
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

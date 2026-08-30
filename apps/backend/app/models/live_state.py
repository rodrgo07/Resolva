from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Boolean, Integer, Float, DateTime, JSON, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class LiveSessionType(str, enum.Enum):
    POMODORO = "POMODORO"
    FOCUS_TIMER = "FOCUS_TIMER"
    ACTIVE_PLANNING_BLOCK = "ACTIVE_PLANNING_BLOCK"
    AGENT_SESSION = "AGENT_SESSION"

class LiveSessionStatus(str, enum.Enum):
    IDLE = "IDLE"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LiveSession(BaseModel):
    __tablename__ = "live_sessions"

    session_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    origin_device_id: Mapped[str] = mapped_column(String(100), default="DESKTOP-MAIN")
    user_id: Mapped[str] = mapped_column(String(100), default="user_default")
    type: Mapped[LiveSessionType] = mapped_column(SQLEnum(LiveSessionType), default=LiveSessionType.POMODORO, index=True)
    status: Mapped[LiveSessionStatus] = mapped_column(SQLEnum(LiveSessionStatus), default=LiveSessionStatus.IDLE, index=True)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    paused_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[int] = mapped_column(Integer, default=1500)
    remaining_seconds: Mapped[int] = mapped_column(Integer, default=1500)
    current_block_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    version: Mapped[int] = mapped_column(Integer, default=1)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_live_sessions_type_status", "type", "status"),
    )

class DevicePresence(BaseModel):
    __tablename__ = "device_presences"

    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    device_name: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(50), default="ANDROID")
    app_version: Mapped[str] = mapped_column(String(50), default="0.1.0")
    is_online: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_heartbeat_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    sync_status: Mapped[str] = mapped_column(String(50), default="SYNCED")
    client_info: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

class RealtimeEventRecord(BaseModel):
    __tablename__ = "realtime_events"

    sequence: Mapped[int] = mapped_column(Integer, autoincrement=True, unique=True, index=True)
    event_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    event_type: Mapped[str] = mapped_column(String(100), index=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class EntityVersion(BaseModel):
    __tablename__ = "entity_versions"

    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    checksum: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    updated_by_device: Mapped[str] = mapped_column(String(100), default="DESKTOP-MAIN")
    last_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_entity_versions_type_id", "entity_type", "entity_id", unique=True),
    )

class ConflictResolutionType(str, enum.Enum):
    AUTO_MERGED = "AUTO_MERGED"
    LOCAL_WON = "LOCAL_WON"
    REMOTE_WON = "REMOTE_WON"
    USER_REQUIRED = "USER_REQUIRED"

class AdvancedConflictRecord(BaseModel):
    __tablename__ = "advanced_sync_conflicts"

    conflict_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    base_version: Mapped[int] = mapped_column(Integer, default=1)
    local_version: Mapped[int] = mapped_column(Integer, default=1)
    remote_version: Mapped[int] = mapped_column(Integer, default=1)
    local_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    remote_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    merged_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    conflict_type: Mapped[str] = mapped_column(String(50), default="CONTENT_CONFLICT")
    resolution: Mapped[ConflictResolutionType] = mapped_column(SQLEnum(ConflictResolutionType), default=ConflictResolutionType.USER_REQUIRED)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    resolved_by_device: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

class EntityRevision(BaseModel):
    __tablename__ = "entity_revisions"

    revision_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True)
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    version: Mapped[int] = mapped_column(Integer, index=True)
    device_id: Mapped[str] = mapped_column(String(100))
    snapshot_payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    change_summary: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

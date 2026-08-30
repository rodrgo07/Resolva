from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class BackupType(str, enum.Enum):
    MANUAL = "MANUAL"
    AUTOMATIC = "AUTOMATIC"
    PRE_MIGRATION = "PRE_MIGRATION"
    PRE_RESTORE = "PRE_RESTORE"

class BackupStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RESTORING = "RESTORING"
    RESTORED = "RESTORED"

class BackupRecord(BaseModel):
    __tablename__ = "backups"

    filename: Mapped[str] = mapped_column(String(255), unique=True)
    filepath: Mapped[str] = mapped_column(String(500))
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    checksum_sha256: Mapped[str] = mapped_column(String(64))
    is_encrypted: Mapped[bool] = mapped_column(Boolean, default=True)
    backup_type: Mapped[BackupType] = mapped_column(SQLEnum(BackupType), default=BackupType.MANUAL)
    status: Mapped[BackupStatus] = mapped_column(SQLEnum(BackupStatus), default=BackupStatus.COMPLETED)
    schema_version: Mapped[str] = mapped_column(String(50), default="0.1.0")
    device_id: Mapped[Optional[str]] = mapped_column(String(100))

class SyncStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CONFLICT = "CONFLICT"
    CANCELLED = "CANCELLED"

class SyncQueue(BaseModel):
    __tablename__ = "sync_queue"

    entity_type: Mapped[str] = mapped_column(String(50)) # tasks, finances, calendar, etc.
    entity_id: Mapped[str] = mapped_column(String(100))
    operation: Mapped[str] = mapped_column(String(20)) # CREATE, UPDATE, DELETE
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON) # Sanitized payload
    status: Mapped[SyncStatusEnum] = mapped_column(SQLEnum(SyncStatusEnum), default=SyncStatusEnum.PENDING)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    max_retries: Mapped[int] = mapped_column(Integer, default=3)
    last_error: Mapped[Optional[str]] = mapped_column(String)

class SyncConflict(BaseModel):
    __tablename__ = "sync_conflicts"

    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[str] = mapped_column(String(100))
    local_version: Mapped[Dict[str, Any]] = mapped_column(JSON)
    remote_version: Mapped[Dict[str, Any]] = mapped_column(JSON)
    device_id: Mapped[str] = mapped_column(String(100))
    resolution: Mapped[str] = mapped_column(String(50), default="LAST_WRITE_WINS")
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=True)

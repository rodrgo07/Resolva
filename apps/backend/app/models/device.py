from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Boolean, Integer, Float, ForeignKey, JSON, Enum as SQLEnum, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class DevicePlatform(str, enum.Enum):
    WINDOWS = "WINDOWS"
    ANDROID = "ANDROID"
    IOS = "IOS"
    WEB = "WEB"
    MACOS = "MACOS"
    LINUX = "LINUX"

class DeviceStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"
    PENDING_PAIR = "PENDING_PAIR"
    OFFLINE = "OFFLINE"

class RemoteActionStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"

class Device(BaseModel):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    device_name: Mapped[str] = mapped_column(String(255))
    platform: Mapped[DevicePlatform] = mapped_column(SQLEnum(DevicePlatform), default=DevicePlatform.ANDROID, index=True)
    app_version: Mapped[str] = mapped_column(String(50), default="0.1.0")
    status: Mapped[DeviceStatus] = mapped_column(SQLEnum(DeviceStatus), default=DeviceStatus.ACTIVE, index=True)
    is_trusted: Mapped[bool] = mapped_column(Boolean, default=True)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    paired_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Metadata adicional (IP local, capabilities, etc.)
    client_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    sessions: Mapped[list["DeviceSession"]] = relationship(back_populates="device", cascade="all, delete-orphan")
    push_tokens: Mapped[list["PushDeviceToken"]] = relationship(back_populates="device", cascade="all, delete-orphan")

class DeviceSession(BaseModel):
    __tablename__ = "device_sessions"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    session_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    refresh_token: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    created_ip: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    device: Mapped["Device"] = relationship(back_populates="sessions")

class PairingRequest(BaseModel):
    __tablename__ = "pairing_requests"

    pairing_code: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    qr_payload: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    nonce: Mapped[str] = mapped_column(String(100), unique=True)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True) # PENDING, CLAIMED, EXPIRED, CANCELLED
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    desktop_device_id: Mapped[str] = mapped_column(String(100), default="RESOLVA-DESKTOP-MAIN")
    server_endpoint: Mapped[str] = mapped_column(String(255), default="http://127.0.0.1:8700")

class SyncOperation(BaseModel):
    __tablename__ = "sync_operations"

    operation_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    entity_type: Mapped[str] = mapped_column(String(50), index=True) # tasks, finances, calendar, studies, notifications
    entity_id: Mapped[str] = mapped_column(String(100), index=True)
    operation: Mapped[str] = mapped_column(String(50), index=True) # CREATE_TASK, UPDATE_TASK, COMPLETE_TASK, etc.
    payload: Mapped[Dict[str, Any]] = mapped_column(JSON)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="APPLIED", index=True) # APPLIED, CONFLICT, REJECTED
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class RemoteCommandRecord(BaseModel):
    __tablename__ = "remote_commands"

    request_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    command_type: Mapped[str] = mapped_column(String(100), index=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    permission_level: Mapped[str] = mapped_column(String(50), default="READ")
    risk_level: Mapped[str] = mapped_column(String(50), default="LOW")
    status: Mapped[str] = mapped_column(String(50), default="EXECUTED", index=True)
    result_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

class RemotePendingAction(BaseModel):
    __tablename__ = "remote_pending_actions"

    action_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    request_id: Mapped[str] = mapped_column(String(100), index=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    command_type: Mapped[str] = mapped_column(String(100), index=True)
    parameters: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    risk_level: Mapped[str] = mapped_column(String(50), default="MEDIUM")
    status: Mapped[RemoteActionStatus] = mapped_column(SQLEnum(RemoteActionStatus), default=RemoteActionStatus.PENDING, index=True)
    description: Mapped[str] = mapped_column(String(500))
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    confirmed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

class PushDeviceToken(BaseModel):
    __tablename__ = "push_device_tokens"

    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id", ondelete="CASCADE"), index=True)
    platform: Mapped[str] = mapped_column(String(50), default="ANDROID")
    push_token: Mapped[str] = mapped_column(String(500), unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_registered_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    device: Mapped["Device"] = relationship(back_populates="push_tokens")

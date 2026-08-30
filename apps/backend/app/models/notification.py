from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"

    type: Mapped[str] = mapped_column(String(100), index=True)
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String(50), default="NORMAL", index=True)
    source: Mapped[str] = mapped_column(String(50), default="SYSTEM", index=True)
    source_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    dedup_key: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    dismissed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    scheduled_for: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    action_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    action_payload: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(50), default="PENDING", index=True)
    
    # Compatibilidade retroativa com campos antigos da Fase 1..26
    action_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    __table_args__ = (
        Index("ix_notifications_status_priority", "status", "priority"),
        Index("ix_notifications_created_at", "created_at"),
    )

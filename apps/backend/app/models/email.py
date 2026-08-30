from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Boolean, ForeignKey, JSON, Index, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class EmailAccount(BaseModel):
    __tablename__ = "email_accounts"

    provider: Mapped[str] = mapped_column(String(100), index=True) # gmail, outlook, mock
    email_address: Mapped[str] = mapped_column(String(255), index=True)
    credentials_encrypted: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    sync_status: Mapped[str] = mapped_column(String(50), default="idle")
    sync_error: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    next_page_token: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    history_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    emails: Mapped[list["Email"]] = relationship(back_populates="account", cascade="all, delete-orphan")

class Email(BaseModel):
    __tablename__ = "emails"

    account_id: Mapped[int] = mapped_column(ForeignKey("email_accounts.id", ondelete="CASCADE"), index=True)
    external_id: Mapped[str] = mapped_column(String(255), index=True)
    thread_id: Mapped[Optional[str]] = mapped_column(String(255), index=True, nullable=True)
    from_address: Mapped[str] = mapped_column(String(255), index=True)
    from_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    to_addresses: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    subject: Mapped[str] = mapped_column(String(500))
    body_preview: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    body_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    body_html: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    is_starred: Mapped[bool] = mapped_column(Boolean, default=False)
    is_important: Mapped[bool] = mapped_column(Boolean, default=False)
    labels: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)
    ai_classification: Mapped[Optional[str]] = mapped_column(String(50), index=True, nullable=True) # CRITICAL, IMPORTANT, NORMAL, LOW, NEWSLETTER
    ai_reasoning: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    needs_reply: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    account: Mapped["EmailAccount"] = relationship(back_populates="emails")

    __table_args__ = (
        Index("ix_emails_account_external", "account_id", "external_id", unique=True),
        Index("ix_emails_received_read", "received_at", "is_read"),
    )

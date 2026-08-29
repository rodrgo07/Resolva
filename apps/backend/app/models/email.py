from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class EmailAccount(BaseModel):
    __tablename__ = "email_accounts"

    provider: Mapped[str] = mapped_column(String(100))
    email_address: Mapped[str] = mapped_column(String(255))
    credentials_encrypted: Mapped[Dict[str, Any]] = mapped_column(JSON)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column()
    
    emails: Mapped[list["Email"]] = relationship(back_populates="account")

class Email(BaseModel):
    __tablename__ = "emails"

    account_id: Mapped[int] = mapped_column(ForeignKey("email_accounts.id"))
    from_address: Mapped[str] = mapped_column(String(255))
    from_name: Mapped[Optional[str]] = mapped_column(String(255))
    subject: Mapped[str] = mapped_column(String(255))
    body_preview: Mapped[Optional[str]] = mapped_column(String)
    received_at: Mapped[datetime] = mapped_column()
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_classification: Mapped[Optional[str]] = mapped_column(String(100))
    needs_reply: Mapped[bool] = mapped_column(Boolean, default=False)
    external_id: Mapped[str] = mapped_column(String(255))
    
    account: Mapped["EmailAccount"] = relationship(back_populates="emails")

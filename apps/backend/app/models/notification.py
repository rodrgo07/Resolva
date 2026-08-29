from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

class Notification(BaseModel):
    __tablename__ = "notifications"

    type: Mapped[str] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(String)
    priority: Mapped[str] = mapped_column(String(50), default="normal")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    read_at: Mapped[Optional[datetime]] = mapped_column()

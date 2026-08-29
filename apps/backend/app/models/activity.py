from typing import Optional, Dict, Any
from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

class ActivityLog(BaseModel):
    __tablename__ = "activity_logs"

    type: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column("metadata", JSON)

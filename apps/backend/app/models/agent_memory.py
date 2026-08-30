from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, Integer, Float, DateTime, JSON, Enum as SQLEnum, Index
from sqlalchemy.orm import Mapped, mapped_column
import enum

from .base import BaseModel

class MemoryType(str, enum.Enum):
    FACT = "FACT"
    PREFERENCE = "PREFERENCE"
    ROUTINE = "ROUTINE"
    BEHAVIOR = "BEHAVIOR"
    DECISION = "DECISION"
    OUTCOME = "OUTCOME"

class MemoryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"
    EXPIRED = "EXPIRED"

class AgentMemoryItem(BaseModel):
    __tablename__ = "agent_memories"

    memory_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    type: Mapped[MemoryType] = mapped_column(SQLEnum(MemoryType), default=MemoryType.FACT, index=True)
    content: Mapped[str] = mapped_column(String(1000))
    source: Mapped[str] = mapped_column(String(100), default="USER_EXPLICIT") # USER_EXPLICIT, INFERRED_PATTERN, OUTCOME_FEEDBACK
    confidence: Mapped[float] = mapped_column(Float, default=0.80) # 0.0 a 1.0
    importance: Mapped[int] = mapped_column(Integer, default=3) # 1 a 5
    status: Mapped[MemoryStatus] = mapped_column(SQLEnum(MemoryStatus), default=MemoryStatus.ACTIVE, index=True)
    
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, index=True)
    last_used_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

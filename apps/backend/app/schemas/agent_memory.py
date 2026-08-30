from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

class AgentMemoryCreateRequest(BaseModel):
    type: str = Field("FACT", description="FACT, PREFERENCE, ROUTINE, BEHAVIOR, DECISION, OUTCOME")
    content: str = Field(..., min_length=2, max_length=1000)
    source: Optional[str] = "USER_EXPLICIT"
    confidence: Optional[float] = 0.90
    importance: Optional[int] = 3
    expires_at: Optional[datetime] = None

class AgentMemoryUpdateRequest(BaseModel):
    content: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[int] = None
    status: Optional[str] = None

class AgentMemoryResponse(BaseModel):
    memory_id: str
    type: str
    content: str
    source: str
    confidence: float
    importance: int
    status: str
    created_at: datetime
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

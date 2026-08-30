from pydantic import BaseModel
from typing import Optional

class AgentMemoryPatchRequest(BaseModel):
    content: Optional[str] = None
    confidence: Optional[float] = None
    importance: Optional[int] = None
    status: Optional[str] = None

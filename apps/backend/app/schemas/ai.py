from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None

class MessageResponse(BaseModel):
    id: int
    role: str
    content: Optional[str]
    tool_calls: Optional[Any] = None
    tool_results: Optional[Any] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    message: str
    conversation_id: int
    tool_calls_made: List[str] = []

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

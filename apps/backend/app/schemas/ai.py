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
    tool_calls: Optional[Dict[str, Any]]
    tool_results: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    message_id: int

class ConversationResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    updated_at: datetime
    messages: List[MessageResponse] = []
    
    model_config = ConfigDict(from_attributes=True)

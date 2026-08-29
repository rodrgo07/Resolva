from typing import Optional, Dict, Any, List
from sqlalchemy import String, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class AIConversation(BaseModel):
    __tablename__ = "ai_conversations"

    title: Mapped[str] = mapped_column(String(255))
    
    messages: Mapped[List["AIMessage"]] = relationship(back_populates="conversation")

class AIMessage(BaseModel):
    __tablename__ = "ai_messages"

    conversation_id: Mapped[int] = mapped_column(ForeignKey("ai_conversations.id"))
    role: Mapped[str] = mapped_column(String(50))
    content: Mapped[Optional[str]] = mapped_column(String)
    tool_calls: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    tool_results: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON)
    
    conversation: Mapped["AIConversation"] = relationship(back_populates="messages")

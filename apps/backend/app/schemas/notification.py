from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class NotificationResponse(BaseModel):
    id: int
    type: str
    title: str
    message: str
    priority: str
    is_read: bool
    action_data: Optional[Dict[str, Any]]
    read_at: Optional[datetime]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class NotificationSummary(BaseModel):
    unread_count: int
    total_count: int

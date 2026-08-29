from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime

class EmailAccountResponse(BaseModel):
    id: int
    provider: str
    email_address: str
    is_active: bool
    last_synced_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)

class EmailResponse(BaseModel):
    id: int
    account_id: int
    from_address: str
    from_name: Optional[str]
    subject: str
    body_preview: Optional[str]
    received_at: datetime
    is_read: bool
    ai_classification: Optional[str]
    needs_reply: bool
    external_id: str
    
    model_config = ConfigDict(from_attributes=True)

class EmailSummary(BaseModel):
    unread_count: int
    needs_reply_count: int
    total_count: int

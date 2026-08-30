from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class EmailAccountResponse(BaseModel):
    id: int
    provider: str
    email_address: str
    is_active: bool
    last_synced_at: Optional[datetime] = None
    sync_status: str = "idle"
    sync_error: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class EmailResponse(BaseModel):
    id: int
    account_id: int
    provider: Optional[str] = None
    external_id: str
    thread_id: Optional[str] = None
    from_address: str
    from_name: Optional[str] = None
    to_addresses: Optional[List[str]] = []
    subject: str
    body_preview: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    received_at: datetime
    is_read: bool
    is_starred: bool = False
    is_important: bool = False
    labels: Optional[List[str]] = []
    ai_classification: Optional[str] = None
    ai_reasoning: Optional[str] = None
    needs_reply: bool = False
    synced_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class EmailListResponse(BaseModel):
    items: List[EmailResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

class EmailSummary(BaseModel):
    unread_count: int
    critical_count: int
    important_count: int
    needs_reply_count: int
    total_count: int

class ConnectOAuthInitResponse(BaseModel):
    authorization_url: str
    state: str
    provider: str

class ConnectOAuthCallbackRequest(BaseModel):
    code: str
    state: str
    code_verifier: Optional[str] = None

class EmailReplyRequest(BaseModel):
    body: str
    confirmed: bool = False

class EmailActionResponse(BaseModel):
    success: bool
    message: str
    email_id: int

from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ActivityResponse(BaseModel):
    id: int
    type: str
    action: str
    description: str
    metadata_json: Optional[Dict[str, Any]]
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

from pydantic import BaseModel, ConfigDict
from typing import Optional

class SettingUpdate(BaseModel):
    value: Optional[str]

class SettingResponse(BaseModel):
    id: int
    key: str
    value: Optional[str]
    type: str
    
    model_config = ConfigDict(from_attributes=True)

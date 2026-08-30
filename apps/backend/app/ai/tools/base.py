from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from app.ai.permissions import PermissionLevel, RiskLevel

class BaseTool(ABC):
    name: str
    description: str
    category: str = "general"
    parameters: Dict[str, Any]
    permission_level: PermissionLevel = PermissionLevel.READ
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    confirmation_message: Optional[str] = None
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        pass

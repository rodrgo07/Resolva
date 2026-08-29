from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseTool(ABC):
    name: str
    description: str
    parameters: Dict[str, Any]
    permission_level: str
    
    @abstractmethod
    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        pass

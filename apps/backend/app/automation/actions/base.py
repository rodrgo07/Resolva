from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ActionResult:
    success: bool
    message: str
    error: Optional[str] = None

class BaseAction(ABC):
    def __init__(self, type: str, config: Dict[str, Any], requires_confirmation: bool = False):
        self.type = type
        self.config = config
        self.requires_confirmation = requires_confirmation
        
    @abstractmethod
    async def execute(self) -> ActionResult:
        pass

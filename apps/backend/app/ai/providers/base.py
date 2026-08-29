from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]

@dataclass
class AIResponse:
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]]
    usage: Dict[str, int]

class AIProvider(ABC):
    @abstractmethod
    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> AIResponse:
        pass

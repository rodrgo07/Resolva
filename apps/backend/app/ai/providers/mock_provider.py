from typing import List, Dict, Any, Optional
import uuid
from app.ai.providers.base import AIProvider, AIResponse, ToolCall

class MockAIProvider(AIProvider):
    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> AIResponse:
        last_msg = messages[-1].get("content", "").lower()
        
        if "quanto gastei" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_finance_summary", arguments={"period": "this_month"})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "tarefas atrasadas" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_overdue_tasks", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
            
        return AIResponse(
            content="Olá! Eu sou o assistente virtual (mock). Como posso ajudar você hoje?",
            tool_calls=None,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

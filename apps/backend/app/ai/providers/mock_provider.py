from typing import List, Dict, Any, Optional
import uuid
from app.ai.providers.base import AIProvider, AIResponse, ToolCall

class MockAIProvider(AIProvider):
    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> AIResponse:
        last_msg_obj = messages[-1]
        last_msg = last_msg_obj.get("content", "").lower()
        role = last_msg_obj.get("role", "")

        # If previous message was a tool result, generate natural response
        if role == "tool":
            return AIResponse(
                content=f"Pronto! Analisei as informações do Resolva: {last_msg_obj.get('content')}",
                tool_calls=None,
                usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
            )

        if "quanto gastei" in last_msg or "finanças" in last_msg or "gastos" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_finance_summary", arguments={"days": 30})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "tarefa" in last_msg or "atrasada" in last_msg or "fazer" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_tasks", arguments={"status": "pendente"})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "estud" in last_msg or "estudei" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_study_summary", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
            
        return AIResponse(
            content="Olá! Eu sou o assistente do Resolva. Posso consultar suas tarefas, finanças e estudos ou ajudar a planejar o seu dia.",
            tool_calls=None,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

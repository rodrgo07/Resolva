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

        # Provider-specific queries
        provider = "all"
        if "gmail" in last_msg:
            provider = "gmail"
        elif "outlook" in last_msg or "microsoft" in last_msg:
            provider = "outlook"

        # Email queries
        if "email importante" in last_msg or "emails importantes" in last_msg or ("urgente" in last_msg and "email" in last_msg):
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_important_emails", arguments={"provider": provider, "limit": 5})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "email não lido" in last_msg or "emails não lidos" in last_msg or "emails pendentes" in last_msg or ("não lido" in last_msg and "email" in last_msg):
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_unread_emails", arguments={"provider": provider, "limit": 5})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif ("resumo" in last_msg and "email" in last_msg) or ("panorama" in last_msg and "email" in last_msg):
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_email_summary", arguments={"provider": provider})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "email" in last_msg or "emails" in last_msg:
            query = "microsoft" if ("microsoft" in last_msg or "outlook" in last_msg) else "pagamento"
            if "sobre " in last_msg:
                query = last_msg.split("sobre ")[1].split()[0].strip()
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="search_emails", arguments={"query": query, "provider": provider})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "arquive" in last_msg and "email" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="archive_email", arguments={"email_id": 1})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # Finances
        elif "quanto gastei" in last_msg or "finanças" in last_msg or "gastos" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_finance_summary", arguments={"days": 30})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        # Tasks
        elif "tarefa" in last_msg or "atrasada" in last_msg or "fazer" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_tasks", arguments={"status": "pendente"})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        # Studies
        elif "estud" in last_msg or "estudei" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_study_summary", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
            
        return AIResponse(
            content="Olá! Eu sou o assistente do Resolva. Posso consultar seus e-mails unificados (Gmail & Outlook), tarefas, finanças e estudos.",
            tool_calls=None,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

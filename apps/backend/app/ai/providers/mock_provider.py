from typing import List, Dict, Any, Optional
import uuid
from app.ai.providers.base import AIProvider, AIResponse, ToolCall

class MockAIProvider(AIProvider):
    """
    Mock AI Provider com suporte completo aos comandos e intenções do Resolva Agent:
    - Organizar o dia / Daily planner
    - Contexto / Tarefas atrasadas / Agenda
    - Finanças estruturadas e recomendações
    - Estudos e Pomodoro
    - E-mails unificados (Gmail & Outlook)
    - Automações seguras
    """
    async def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> AIResponse:
        last_msg_obj = messages[-1]
        last_msg = last_msg_obj.get("content", "").lower()
        role = last_msg_obj.get("role", "")

        # Resposta após execução de Tool
        if role == "tool":
            return AIResponse(
                content=f"Análise concluída pelo Resolva Agent: {last_msg_obj.get('content')}",
                tool_calls=None,
                usage={"prompt_tokens": 15, "completion_tokens": 25, "total_tokens": 40}
            )

        # 1. Organizar dia / Planejador diário
        if "organiz" in last_msg or "planej" in last_msg or "meu dia" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="organize_my_day", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 2. Contexto de Hoje / O que preciso fazer agora
        if "o que preciso fazer" in last_msg or "o que tenho" in last_msg or "resumo do dia" in last_msg or "hoje" in last_msg and "contexto" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_today_context", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 3. Tarefas atrasadas / Pendências
        if "atrasad" in last_msg or "pendênc" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_overdue_tasks", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 4. Compromissos e Agenda
        if "compromisso" in last_msg or "agenda" in last_msg or "evento" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_upcoming_events", arguments={"days_ahead": 3})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 5. E-mails (Gmail & Outlook)
        provider = "all"
        if "gmail" in last_msg:
            provider = "gmail"
        elif "outlook" in last_msg or "microsoft" in last_msg:
            provider = "outlook"

        if "email importante" in last_msg or "emails importantes" in last_msg or ("urgente" in last_msg and "email" in last_msg):
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_important_emails", arguments={"provider": provider, "limit": 5})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif "email não lido" in last_msg or "emails não lidos" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_unread_emails", arguments={"provider": provider, "limit": 5})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )
        elif ("resumo" in last_msg and "email" in last_msg):
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

        # 6. Finanças
        if "quanto gastei" in last_msg or "finanças" in last_msg or "gastos" in last_msg or "posso gastar" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_finance_summary", arguments={"days": 30})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 7. Estudos
        if "estud" in last_msg or "pomodoro" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="get_study_summary", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 8. Automações
        if "automação" in last_msg or "automações" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="list_automations", arguments={})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        # 9. Concluir Tarefa
        if "conclua a tarefa" in last_msg or "concluir tarefa" in last_msg or "termine a tarefa" in last_msg:
            return AIResponse(
                content=None,
                tool_calls=[ToolCall(id=str(uuid.uuid4()), name="complete_task", arguments={"task_id": 1})],
                usage={"prompt_tokens": 10, "completion_tokens": 15, "total_tokens": 25}
            )

        return AIResponse(
            content="Olá! Eu sou o Resolva Agent. Posso organizar seu dia, consultar pendências, triar e-mails e resumir finanças.",
            tool_calls=None,
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )

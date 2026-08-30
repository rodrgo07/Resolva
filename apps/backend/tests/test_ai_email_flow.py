import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.ai.orchestrator import AIOrchestrator

@pytest.mark.asyncio
async def test_ai_email_tools_execution():
    async with async_session_maker() as session:
        orchestrator = AIOrchestrator(db=session)
        
        # 1. Testar consulta por emails importantes no Gmail
        res1 = await orchestrator.process_message("Resolva, quais emails importantes eu tenho no Gmail?")
        assert res1.message is not None
        assert "list_important_emails" in res1.tool_calls_made

        # 2. Testar consulta por emails do Outlook
        res2 = await orchestrator.process_message("Mostre meus emails do Outlook")
        assert res2.message is not None
        assert "search_emails" in res2.tool_calls_made or "get_unread_emails" in res2.tool_calls_made or "list_important_emails" in res2.tool_calls_made

        # 3. Testar busca por termo específico
        res3 = await orchestrator.process_message("Pesquise emails sobre pagamento")
        assert res3.message is not None
        assert "search_emails" in res3.tool_calls_made

        # 4. Testar resumo unificado
        res4 = await orchestrator.process_message("Mostre o resumo dos meus emails")
        assert res4.message is not None
        assert "get_email_summary" in res4.tool_calls_made

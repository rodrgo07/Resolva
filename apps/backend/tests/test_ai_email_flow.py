import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.ai.orchestrator import AIOrchestrator

@pytest.mark.asyncio
async def test_ai_email_tools_execution():
    async with async_session_maker() as session:
        orchestrator = AIOrchestrator(db=session)
        
        # 1. Testar consulta por emails importantes
        res1 = await orchestrator.process_message("Resolva, quais emails importantes eu tenho?")
        assert res1.message is not None
        assert "list_important_emails" in res1.tool_calls_made

        # 2. Testar busca por termo
        res2 = await orchestrator.process_message("Pesquise emails sobre pagamento")
        assert res2.message is not None
        assert "search_emails" in res2.tool_calls_made

        # 3. Testar resumo geral
        res3 = await orchestrator.process_message("Mostre o resumo dos meus emails")
        assert res3.message is not None
        assert "get_email_summary" in res3.tool_calls_made

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.ai.orchestrator import ResolvaAgent
from app.ai.permissions import check_permission, PermissionLevel, RiskLevel
from app.ai.tools.agent_tools import (
    GetTodayContextTool, OrganizeDayTool, GetOverdueTasksTool,
    CompleteTaskTool, DeleteTaskTool, ExecuteAutomationTool
)

@pytest.mark.asyncio
async def test_permission_layer_enforcement():
    # 1. READ tool: executa livremente sem confirmação
    read_tool = GetTodayContextTool()
    assert check_permission(read_tool, {"confirmed": False}) == True

    # 2. WRITE / MEDIUM risk: bloqueia se confirmed=False
    write_tool = CompleteTaskTool()
    assert write_tool.requires_confirmation == True
    assert check_permission(write_tool, {"confirmed": False}) == False
    assert check_permission(write_tool, {"confirmed": True}) == True

    # 3. EXECUTE / HIGH risk: automação requer confirmed=True
    exec_tool = ExecuteAutomationTool()
    assert exec_tool.risk_level == RiskLevel.HIGH
    assert check_permission(exec_tool, {"confirmed": False}) == False
    assert check_permission(exec_tool, {"confirmed": True}) == True

@pytest.mark.asyncio
async def test_agent_context_and_planner():
    async with async_session_maker() as session:
        agent = ResolvaAgent(db=session)

        # Contexto
        ctx_tool = GetTodayContextTool()
        ctx = await ctx_tool.execute({}, {"db": session})
        assert "tasks_summary" in ctx
        assert "calendar_summary" in ctx
        assert "emails_summary" in ctx

        # Planejador Diário
        plan_tool = OrganizeDayTool()
        plan = await plan_tool.execute({}, {"db": session})
        assert "high_priority" in plan
        assert "time_blocks" in plan
        assert "recommendations" in plan

@pytest.mark.asyncio
async def test_agent_chat_and_tools_flow():
    async with async_session_maker() as session:
        agent = ResolvaAgent(db=session)

        # 1. Organizar dia
        res1 = await agent.process_message("Resolva, organize meu dia")
        assert res1.message is not None
        assert "organize_my_day" in res1.tool_calls_made

        # 2. Consultar tarefas atrasadas
        res2 = await agent.process_message("Tenho tarefas atrasadas?")
        assert res2.message is not None
        assert "get_overdue_tasks" in res2.tool_calls_made

        # 3. Consultar compromissos
        res3 = await agent.process_message("Quais são meus compromissos na agenda?")
        assert res3.message is not None
        assert "get_upcoming_events" in res3.tool_calls_made

@pytest.mark.asyncio
async def test_agent_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Contexto do dia
        ctx_res = await ac.get("/api/ai/context/today")
        assert ctx_res.status_code == 200
        assert "tasks_summary" in ctx_res.json()

        # 2. Plano do dia
        plan_res = await ac.get("/api/ai/planner/today")
        assert plan_res.status_code == 200
        assert "time_blocks" in plan_res.json()

        # 3. Atividades do Agent
        act_res = await ac.get("/api/ai/activity")
        assert act_res.status_code == 200
        assert isinstance(act_res.json(), list)

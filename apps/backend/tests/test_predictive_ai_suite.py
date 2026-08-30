import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.ai.context_engine import ContextEngine
from app.ai.memory import AgentMemoryManager
from app.ai.pattern_engine import PatternEngine
from app.ai.prediction_engine import PredictionEngine
from app.ai.planner import PlanningEngine

@pytest.mark.asyncio
async def test_memory_engine_crud_and_clear():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Criação de memória contextual
        res_create = await ac.post("/api/ai/memories/", json={
            "type": "PREFERENCE",
            "content": "Prefere sessões de estudo de 25 minutos com modo Pomodoro.",
            "source": "USER_EXPLICIT",
            "confidence": 0.95,
            "importance": 4
        })
        assert res_create.status_code == 201
        mem_data = res_create.json()
        assert mem_data["type"] == "PREFERENCE"
        memory_id = mem_data["memory_id"]

        # 2. Listagem de memórias
        res_list = await ac.get("/api/ai/memories/?type=PREFERENCE")
        assert res_list.status_code == 200
        items = res_list.json()
        assert any(m["memory_id"] == memory_id for m in items)

        # 3. PATCH (Atualização parcial)
        res_patch = await ac.patch(f"/api/ai/memories/{memory_id}", json={
            "importance": 5,
            "confidence": 0.99
        })
        assert res_patch.status_code == 200
        assert res_patch.json()["importance"] == 5
        assert res_patch.json()["confidence"] == 0.99

        # 4. Exclusão individual
        res_del = await ac.delete(f"/api/ai/memories/{memory_id}")
        assert res_del.status_code == 200

        # 4. Limpeza total de memórias (Confirmação explícita)
        res_clear = await ac.post("/api/ai/memories/clear-all")
        assert res_clear.status_code == 200

@pytest.mark.asyncio
async def test_pattern_and_prediction_engines():
    async with async_session_maker() as session:
        pattern_eng = PatternEngine(session)
        patterns = await pattern_eng.analyze_productivity_patterns()
        assert "tasks_completion_rate_pct" in patterns
        assert "best_focus_window" in patterns
        assert "detected_habits" in patterns

        prediction_eng = PredictionEngine(session, pattern_eng)
        predictions = await prediction_eng.generate_predictions()
        assert "suggested_focus_window" in predictions
        assert "proactive_recommendations" in predictions

@pytest.mark.asyncio
async def test_predictive_planning_engine_with_predictions():
    async with async_session_maker() as session:
        ctx_engine = ContextEngine(session)
        memory_mgr = AgentMemoryManager(session)
        pattern_eng = PatternEngine(session)
        prediction_eng = PredictionEngine(session, pattern_eng)
        planner = PlanningEngine(ctx_engine, memory_mgr, prediction_eng)

        plan = await planner.generate_daily_plan("Rodrigo")
        assert "high_priority" in plan
        assert "time_blocks" in plan
        assert "recommendations" in plan
        assert "predictions_summary" in plan

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data

@pytest.mark.asyncio
async def test_tasks_crud_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Create
        create_res = await ac.post("/api/tasks/", json={
            "title": "Test Task Automated",
            "priority": "alta",
            "status": "pendente"
        })
        assert create_res.status_code == 201
        created = create_res.json()
        task_id = created["id"]

        # 2. Get list
        list_res = await ac.get("/api/tasks/")
        assert list_res.status_code == 200
        assert any(t["id"] == task_id for t in list_res.json())

        # 3. Complete
        comp_res = await ac.post(f"/api/tasks/{task_id}/complete")
        assert comp_res.status_code == 200
        assert comp_res.json()["status"] == "concluida"

        # 4. Delete
        del_res = await ac.delete(f"/api/tasks/{task_id}")
        assert del_res.status_code == 204

@pytest.mark.asyncio
async def test_finances_crud_and_summary():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Create an expense
        create_res = await ac.post("/api/finances/transactions", json={
            "amount": 75.50,
            "description": "Lanche Teste",
            "type": "expense",
            "date": "2026-08-29"
        })
        assert create_res.status_code == 201
        trans_id = create_res.json()["id"]

        # Summary
        summary_res = await ac.get("/api/finances/summary")
        assert summary_res.status_code == 200
        assert summary_res.json()["total_income"] >= 0

        # Delete
        del_res = await ac.delete(f"/api/finances/transactions/{trans_id}")
        assert del_res.status_code == 204

@pytest.mark.asyncio
async def test_studies_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        subjects_res = await ac.get("/api/studies/subjects")
        assert subjects_res.status_code == 200
        assert len(subjects_res.json()) > 0

        summary_res = await ac.get("/api/studies/summary")
        assert summary_res.status_code == 200
        assert "hours_this_week" in summary_res.json()

@pytest.mark.asyncio
async def test_ai_chat_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        chat_res = await ac.post("/api/ai/chat", json={
            "message": "Quanto gastei essa semana?"
        })
        assert chat_res.status_code == 200
        data = chat_res.json()
        assert "message" in data
        assert "conversation_id" in data

@pytest.mark.asyncio
async def test_automations_run():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        list_res = await ac.get("/api/automations/")
        assert list_res.status_code == 200
        autos = list_res.json()
        if autos:
            auto_id = autos[0]["id"]
            run_res = await ac.post(f"/api/automations/{auto_id}/run")
            assert run_res.status_code == 200
            assert run_res.json()["status"] in ["completed", "running", "failed"]

@pytest.mark.asyncio
async def test_notifications_and_activity():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        notifs_res = await ac.get("/api/notifications/")
        assert notifs_res.status_code == 200
        assert len(notifs_res.json()) > 0

        act_res = await ac.get("/api/activity/")
        assert act_res.status_code == 200
        assert len(act_res.json()) > 0

@pytest.mark.asyncio
async def test_global_search():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        search_res = await ac.get("/api/search/?q=Resolva")
        assert search_res.status_code == 200
        results = search_res.json()
        assert "results" in results

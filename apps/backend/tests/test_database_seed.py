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
async def test_tasks_from_seed():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/tasks/")
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 4
    titles = [t["title"] for t in tasks]
    assert "Finalizar arquitetura do Resolva" in titles

@pytest.mark.asyncio
async def test_finances_summary_from_seed():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/finances/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_income"] >= 3500.00
    assert summary["total_expense"] > 0
    assert summary["balance"] == summary["total_income"] - summary["total_expense"]

@pytest.mark.asyncio
async def test_studies_subjects_from_seed():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/studies/subjects")
    assert response.status_code == 200
    subjects = response.json()
    assert len(subjects) >= 3
    names = [s["name"] for s in subjects]
    assert "Rust & Tauri" in names

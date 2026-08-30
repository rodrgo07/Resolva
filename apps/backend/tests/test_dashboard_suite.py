import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.services.dashboard_service import DashboardService

@pytest.mark.asyncio
async def test_dashboard_service_overview_and_now():
    async with async_session_maker() as session:
        service = DashboardService(session)

        # 1. Overview
        overview = await service.get_overview()
        assert "tasks" in overview
        assert "calendar" in overview
        assert "emails" in overview
        assert "studies" in overview
        assert "finances" in overview
        assert "automations" in overview

        # 2. Card AGORA
        now_card = await service.get_now_card()
        assert "title" in now_card
        assert "badge" in now_card
        assert "action_label" in now_card

        # 3. Timeline
        timeline = await service.get_timeline()
        assert isinstance(timeline, list)
        assert len(timeline) > 0
        assert "time" in timeline[0]

        # 4. Recomendações
        recs = await service.get_recommendations()
        assert isinstance(recs, list)

@pytest.mark.asyncio
async def test_dashboard_api_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Overview
        res_ov = await ac.get("/api/dashboard/overview")
        assert res_ov.status_code == 200
        assert "tasks" in res_ov.json()

        # Now card
        res_now = await ac.get("/api/dashboard/now")
        assert res_now.status_code == 200
        assert "title" in res_now.json()

        # Timeline
        res_tl = await ac.get("/api/dashboard/timeline")
        assert res_tl.status_code == 200
        assert len(res_tl.json()) > 0

        # Recommendations
        res_rec = await ac.get("/api/dashboard/recommendations")
        assert res_rec.status_code == 200
        assert isinstance(res_rec.json(), list)

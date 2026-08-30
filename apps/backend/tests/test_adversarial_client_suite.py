import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.database import async_session_maker
from app.models.device import Device, DeviceStatus, DevicePlatform
from app.models.task import Task
from app.ai.autonomy_policy import AutonomyPolicyEngine
from datetime import datetime

@pytest.mark.asyncio
async def test_client_cannot_bypass_device_authentication():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/remote/commands", json={
            "command_type": "CREATE_TASK",
            "device_id": "ROGUE-ATTACKER-DEV",
            "request_id": "req-rogue-001",
            "payload": {"title": "Malicious Task"}
        })
        assert res.status_code == 403
        assert "não autorizado" in res.json()["detail"]

@pytest.mark.asyncio
async def test_client_cannot_execute_unhomologated_remote_command():
    async with async_session_maker() as db:
        from sqlalchemy import select
        stmt = select(Device).where(Device.device_id == "DEV-TEST-ADV-001")
        res = await db.execute(stmt)
        dev = res.scalar_one_or_none()
        if not dev:
            dev = Device(
                device_id="DEV-TEST-ADV-001",
                device_name="Test Phone",
                platform=DevicePlatform.ANDROID,
                paired_at=datetime.utcnow(),
                status=DeviceStatus.ACTIVE,
                is_trusted=True
            )
            db.add(dev)
            await db.commit()


    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/remote/commands", json={
            "command_type": "DROP_DATABASE_NOW",
            "device_id": "DEV-TEST-ADV-001",
            "request_id": "req-rogue-002",
            "payload": {}
        })
        assert res.status_code in [400, 403, 422]
        assert "não homologado" in res.json()["detail"]


@pytest.mark.asyncio
async def test_client_cannot_forge_risk_or_confirmation():
    async with async_session_maker() as db:
        t = Task(title="Task to Delete")
        db.add(t)
        await db.commit()
        await db.refresh(t)
        t_id = t.id

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/remote/commands", json={
            "command_type": "DELETE_TASK",
            "device_id": "DEV-TEST-001",
            "request_id": "req-rogue-003",
            "payload": {"task_id": t_id, "risk": "LOW", "confirmed": True}
        })
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "PENDING_CONFIRMATION"
        assert data["action_id"] is not None


@pytest.mark.asyncio
async def test_safe_mode_blocks_malicious_write_requests():
    AutonomyPolicyEngine.GLOBAL_SAFE_MODE = True
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/remote/commands", json={
            "command_type": "CREATE_TASK",
            "device_id": "DEV-TEST-001",
            "request_id": "req-rogue-004",
            "payload": {"title": "Task during safe mode"}
        })
        assert res.status_code == 403 or "SAFE_MODE" in res.json().get("detail", "")
    AutonomyPolicyEngine.GLOBAL_SAFE_MODE = False

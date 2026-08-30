import pytest
from httpx import ASGITransport, AsyncClient
from datetime import datetime, timedelta, date

from app.main import app
from app.database import async_session_maker
from app.models.device import Device, PairingRequest, SyncOperation, DeviceStatus
from app.models.task import Task
from app.models.finance import Expense
from app.services.device_manager import DeviceManager
from app.services.mobile_sync_engine import MobileSyncEngine
from app.schemas.device import PairingCompleteRequest, SyncPushItem

@pytest.mark.asyncio
async def test_pairing_flow_expiration_and_single_use():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Desktop inicia pareamento
        start_res = await ac.post("/api/devices/pair/start?server_endpoint=http://192.168.1.100:8700")
        assert start_res.status_code == 200
        start_data = start_res.json()
        assert "pairing_code" in start_data
        assert "qr_payload" in start_data
        assert len(start_data["pairing_code"]) == 6
        code = start_data["pairing_code"]
        nonce = start_data["nonce"]

        # 2. Mobile conclui pareamento
        complete_payload = {
            "pairing_code": code,
            "nonce": nonce,
            "device_name": "Galaxy S24 Ultra",
            "platform": "ANDROID",
            "app_version": "0.1.0"
        }
        comp_res = await ac.post("/api/devices/pair/complete", json=complete_payload)
        assert comp_res.status_code == 200
        comp_data = comp_res.json()
        assert comp_data["success"] == True
        assert "session_token" in comp_data
        assert "refresh_token" in comp_data
        mobile_device_id = comp_data["device_id"]

        # 3. Tentar usar o mesmo código de pareamento novamente (Single-use check)
        reuse_res = await ac.post("/api/devices/pair/complete", json=complete_payload)
        assert reuse_res.status_code == 422 # Código já foi consumido

        # 4. Listagem de dispositivos no Desktop
        list_res = await ac.get("/api/devices")
        assert list_res.status_code == 200
        devices = list_res.json()
        assert any(d["device_id"] == mobile_device_id for d in devices)

        # 5. Renomear dispositivo
        ren_res = await ac.patch(f"/api/devices/{mobile_device_id}", json={"device_name": "Galaxy Rodrigo"})
        assert ren_res.status_code == 200
        assert ren_res.json()["device_name"] == "Galaxy Rodrigo"

        # 6. Revogação de dispositivo
        rev_res = await ac.post(f"/api/devices/{mobile_device_id}/revoke")
        assert rev_res.status_code == 200

        # Dispositivo revogado não deve constar na listagem de ativos
        list_after = await ac.get("/api/devices")
        assert not any(d["device_id"] == mobile_device_id for d in list_after.json())

@pytest.mark.asyncio
async def test_mobile_sync_push_pull_and_idempotency():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        import uuid
        uid = uuid.uuid4().hex[:6]
        device_id = f"RESOLVA-MOBILE-TEST-{uid}"
        op_id_1 = f"op_task_create_{uid}_1"
        op_id_2 = f"op_expense_create_{uid}_2"

        push_payload = {
            "device_id": device_id,
            "operations": [
                {
                    "operation_id": op_id_1,
                    "device_id": device_id,
                    "entity_type": "tasks",
                    "entity_id": "temp_task_1",
                    "operation": "CREATE_TASK",
                    "payload": {
                        "title": "Comprar passagens aéreas",
                        "priority": "alta",
                        "due_date": "2026-10-15"
                    },
                    "version": 1
                },
                {
                    "operation_id": op_id_2,
                    "device_id": device_id,
                    "entity_type": "finances",
                    "entity_id": "temp_exp_1",
                    "operation": "CREATE_EXPENSE",
                    "payload": {
                        "description": "Almoço de negócios",
                        "amount": 85.50,
                        "type": "expense"
                    },
                    "version": 1
                }
            ]
        }

        # 1. Envio de Push inicial
        res_push = await ac.post("/api/sync/push", json=push_payload)
        assert res_push.status_code == 200
        data_push = res_push.json()
        assert data_push["applied_count"] == 2
        assert op_id_1 in data_push["processed_operation_ids"]

        # 2. Reenvio da mesma operação (Idempotência)
        res_push_dup = await ac.post("/api/sync/push", json=push_payload)
        assert res_push_dup.status_code == 200
        data_push_dup = res_push_dup.json()
        # Não aplica novamente no banco, mas confirma processamento
        assert data_push_dup["applied_count"] == 0
        assert op_id_1 in data_push_dup["processed_operation_ids"]

        # 3. Pull das operações por outro dispositivo
        other_device = "RESOLVA-DESKTOP-MAIN"
        pull_payload = {
            "device_id": other_device,
            "limit": 10
        }
        res_pull = await ac.post("/api/sync/pull", json=pull_payload)
        assert res_pull.status_code == 200
        pull_data = res_pull.json()
        assert len(pull_data["operations"]) >= 2
        assert any(o["operation_id"] == op_id_1 for o in pull_data["operations"])

@pytest.mark.asyncio
async def test_mobile_bootstrap_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        res = await ac.get("/api/mobile/bootstrap")
        assert res.status_code == 200
        data = res.json()
        assert "desktop_status" in data
        assert "tasks_count" in data
        assert "events_count" in data
        assert "unread_notifications_count" in data
        assert data["desktop_status"]["backend"] == "ONLINE"

import pytest
import uuid
from httpx import ASGITransport, AsyncClient
from datetime import datetime, timedelta, date

from app.main import app
from app.database import async_session_maker
from app.models.device import Device, DeviceStatus, RemoteActionStatus
from app.models.automation import Automation
from app.models.task import Task
from app.services.event_bus import event_bus

@pytest.mark.asyncio
async def test_remote_commands_execution_and_idempotency():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Pareamento prévio do dispositivo
        pair_start = await ac.post("/api/devices/pair/start")
        code = pair_start.json()["pairing_code"]
        nonce = pair_start.json()["nonce"]
        
        pair_comp = await ac.post("/api/devices/pair/complete", json={
            "pairing_code": code,
            "nonce": nonce,
            "device_name": "Galaxy Remote",
            "platform": "ANDROID",
            "app_version": "0.1.0"
        })
        device_id = pair_comp.json()["device_id"]
        req_id = f"req_{uuid.uuid4().hex[:8]}"

        # 2. Comando Remoto Homologado (CREATE_TASK)
        cmd_payload = {
            "request_id": req_id,
            "device_id": device_id,
            "command_type": "CREATE_TASK",
            "parameters": {
                "title": "Comprar passagem para São Paulo",
                "priority": "alta"
            }
        }
        res_cmd = await ac.post("/api/remote/commands", json=cmd_payload)
        assert res_cmd.status_code == 200
        data_cmd = res_cmd.json()
        assert data_cmd["success"] == True
        assert data_cmd["status"] == "EXECUTED"
        assert "task_id" in data_cmd["data"]

        # 3. Idempotência / Proteção contra Replay
        res_dup = await ac.post("/api/remote/commands", json=cmd_payload)
        assert res_dup.status_code == 200
        assert res_dup.json()["status"] == "EXECUTED"

        # 4. Bloqueio de Comandos Não Homologados (Shell / PowerShell / SQL)
        bad_payload = {
            "request_id": f"req_bad_{uuid.uuid4().hex[:8]}",
            "device_id": device_id,
            "command_type": "EXECUTE_POWERSHELL_SCRIPT",
            "parameters": {"script": "Get-Process"}
        }
        res_bad = await ac.post("/api/remote/commands", json=bad_payload)
        assert res_bad.status_code in [403, 422]

@pytest.mark.asyncio
async def test_remote_action_confirmation_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # Pareamento
        pair_start = await ac.post("/api/devices/pair/start")
        code = pair_start.json()["pairing_code"]
        nonce = pair_start.json()["nonce"]
        
        pair_comp = await ac.post("/api/devices/pair/complete", json={
            "pairing_code": code,
            "nonce": nonce,
            "device_name": "Pixel Remote",
            "platform": "ANDROID"
        })
        device_id = pair_comp.json()["device_id"]

        # Cria automação de teste no banco
        async with async_session_maker() as session:
            auto = Automation(
                name="Rotina Noturna",
                description="Desliga luzes e organiza tarefas",
                is_active=True
            )
            session.add(auto)
            await session.commit()
            auto_id = auto.id

        # Dispara comando que exige confirmação (EXECUTE_APPROVED_AUTOMATION)
        req_id = f"req_confirm_{uuid.uuid4().hex[:8]}"
        confirm_cmd = {
            "request_id": req_id,
            "device_id": device_id,
            "command_type": "EXECUTE_APPROVED_AUTOMATION",
            "parameters": {"automation_id": auto_id}
        }
        res_req = await ac.post("/api/remote/commands", json=confirm_cmd)
        assert res_req.status_code == 200
        res_data = res_req.json()
        assert res_data["status"] == "PENDING_CONFIRMATION"
        assert "action_id" in res_data
        action_id = res_data["action_id"]

        # Lista ações pendentes
        list_pending = await ac.get(f"/api/remote/actions/pending?device_id={device_id}")
        assert list_pending.status_code == 200
        assert any(a["action_id"] == action_id for a in list_pending.json())

        # Confirmação da ação remota
        confirm_res = await ac.post("/api/remote/actions/confirm", json={
            "device_id": device_id,
            "action_id": action_id,
            "confirmed": True
        })
        assert confirm_res.status_code == 200
        assert confirm_res.json()["status"] == "EXECUTED"

@pytest.mark.asyncio
async def test_desktop_status_and_push_tokens():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Desktop Status espelhado
        st_res = await ac.get("/api/remote/desktop/status")
        assert st_res.status_code == 200
        st_data = st_res.json()
        assert st_data["desktop_online"] == True
        assert st_data["backend_status"] == "ONLINE"
        assert "kill_switch_active" in st_data

        # 2. Pareamento para testar push token
        pair_start = await ac.post("/api/devices/pair/start")
        code = pair_start.json()["pairing_code"]
        nonce = pair_start.json()["nonce"]
        pair_comp = await ac.post("/api/devices/pair/complete", json={
            "pairing_code": code,
            "nonce": nonce,
            "device_name": "Push Device",
            "platform": "ANDROID"
        })
        device_id = pair_comp.json()["device_id"]

        # 3. Registro de Push Token
        tok_res = await ac.post(f"/api/remote/devices/{device_id}/push-token", json={
            "platform": "ANDROID",
            "push_token": "ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]"
        })
        assert tok_res.status_code == 200
        assert tok_res.json()["success"] == True

        # 4. Desativação de Push Token
        del_res = await ac.delete(f"/api/remote/devices/{device_id}/push-token")
        assert del_res.status_code == 200
        assert del_res.json()["success"] == True

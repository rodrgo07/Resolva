import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_push_notifications_registration_and_revocation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Pareia dispositivo
        pair_start = await ac.post("/api/devices/pair/start")
        code = pair_start.json()["pairing_code"]
        nonce = pair_start.json()["nonce"]
        pair_comp = await ac.post("/api/devices/pair/complete", json={
            "pairing_code": code,
            "nonce": nonce,
            "device_name": "Test Push Android",
            "platform": "ANDROID"
        })
        device_id = pair_comp.json()["device_id"]

        # 2. Registra Expo push token
        reg_res = await ac.post(f"/api/remote/devices/{device_id}/push-token", json={
            "platform": "ANDROID",
            "push_token": "ExponentPushToken[AbCdEf1234567890]"
        })
        assert reg_res.status_code == 200
        assert reg_res.json()["success"] == True

        # 3. Re-registro idempotente
        reg_res_dup = await ac.post(f"/api/remote/devices/{device_id}/push-token", json={
            "platform": "ANDROID",
            "push_token": "ExponentPushToken[AbCdEf1234567890]"
        })
        assert reg_res_dup.status_code == 200

        # 4. Desativação
        unreg_res = await ac.delete(f"/api/remote/devices/{device_id}/push-token")
        assert unreg_res.status_code == 200

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.models.settings import AppSetting
from app.automation.security import check_action_safety, ALLOWED_WINDOWS_APPS
from app.automation.permissions import AutomationPermissionService
from app.automation.actions_engine import ActionEngine
from app.ai.orchestrator import ResolvaAgent
from app.ai.tools.agent_tools import (
    GetSystemStatusTool, OpenAllowedApplicationTool, ShowNotificationTool,
    FocusResolvaTool, OpenCommandPaletteTool
)
from sqlalchemy import select

@pytest.mark.asyncio
async def test_windows_settings_crud_and_persistence():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Atualizar configuração de startup
        res_startup = await ac.put("/api/settings/windows.startup_enabled", json={"value": "true"})
        assert res_startup.status_code == 200
        assert res_startup.json()["value"] == "true"

        # 2. Atualizar close_behavior
        res_close = await ac.put("/api/settings/windows.close_behavior", json={"value": "minimize_to_tray"})
        assert res_close.status_code == 200
        assert res_close.json()["value"] == "minimize_to_tray"

        # 3. Atualizar hotkey customizado
        res_hk = await ac.put("/api/settings/hotkeys.command_palette", json={"value": "Ctrl+Space"})
        assert res_hk.status_code == 200
        assert res_hk.json()["value"] == "Ctrl+Space"

        # 4. Verificar persistência em banco
        res_get = await ac.get("/api/settings/windows.startup_enabled")
        assert res_get.status_code == 200
        assert res_get.json()["value"] == "true"

@pytest.mark.asyncio
async def test_windows_ai_tools_layer():
    async with async_session_maker() as session:
        agent = ResolvaAgent(db=session)

        # 1. GetSystemStatusTool
        sys_tool = GetSystemStatusTool()
        status_data = await sys_tool.execute({}, {"db": session})
        assert status_data["status"] == "online"
        assert "automations_kill_switch" in status_data
        assert status_data["os"] == "windows"

        # 2. ShowNotificationTool
        notif_tool = ShowNotificationTool()
        notif_res = await notif_tool.execute({
            "title": "Compromisso em 15 minutos",
            "message": "Reunião de alinhamento com a equipe.",
            "type": "calendar"
        }, {"db": session})
        assert notif_res["success"] == True
        assert notif_res["title"] == "Compromisso em 15 minutos"

        # 3. FocusResolvaTool & OpenCommandPaletteTool
        focus_tool = FocusResolvaTool()
        f_res = await focus_tool.execute({}, {})
        assert f_res["success"] == True

        palette_tool = OpenCommandPaletteTool()
        p_res = await palette_tool.execute({}, {})
        assert p_res["success"] == True

@pytest.mark.asyncio
async def test_windows_security_whitelist_and_blocks():
    # 1. App na whitelist permitido
    safe_app = {"type": "OPEN_APPLICATION", "config": {"app_name": "vscode"}}
    is_safe, msg = check_action_safety(safe_app)
    assert is_safe == True

    # 2. App fora da whitelist bloqueado
    bad_app = {"type": "OPEN_APPLICATION", "config": {"app_name": "malware.exe"}}
    is_safe_bad, reason = check_action_safety(bad_app)
    assert is_safe_bad == False
    assert "whitelist" in reason.lower()

    # 3. Tentativa de shell injection bloqueada
    shell_attempt = {"type": "SHOW_NOTIFICATION", "config": {"title": "Test", "message": "cmd.exe /c calc"}}
    is_safe_inj, _ = check_action_safety(shell_attempt)
    assert is_safe_inj == False

    # 4. Ações nativas registradas na whitelist
    for act in ["SHOW_NOTIFICATION", "OPEN_RESOLVA", "OPEN_COMMAND_PALETTE", "CREATE_BACKUP", "SYNC_NOW"]:
        assert check_action_safety({"type": act, "config": {}})[0] == True

@pytest.mark.asyncio
async def test_action_engine_windows_actions():
    async with async_session_maker() as session:
        engine = ActionEngine(session)

        # 1. SHOW_NOTIFICATION
        ok_notif, log_notif = await engine.execute_action("SHOW_NOTIFICATION", {
            "title": "Pomodoro Terminado",
            "message": "Hora de fazer uma pausa de 5 minutos."
        })
        assert ok_notif == True
        assert "sucesso" in log_notif.lower()

        # 2. OPEN_RESOLVA & OPEN_COMMAND_PALETTE
        ok_res, _ = await engine.execute_action("OPEN_RESOLVA", {})
        assert ok_res == True

        ok_pal, _ = await engine.execute_action("OPEN_COMMAND_PALETTE", {})
        assert ok_pal == True

        # 3. SYNC_NOW
        ok_sync, _ = await engine.execute_action("SYNC_NOW", {})
        assert ok_sync == True

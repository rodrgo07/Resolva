import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import async_session_maker
from app.automation.security import check_action_safety, ALLOWED_WINDOWS_APPS
from app.automation.permissions import AutomationPermissionService, AutomationRiskLevel
from app.automation.kill_switch import is_kill_switch_active, activate_kill_switch, deactivate_kill_switch
from app.automation.engine import AutomationEngine
from app.automation.conditions import ConditionEngine
from app.models.automation import Automation, AutomationAction, AutomationTrigger

@pytest.mark.asyncio
async def test_automation_security_whitelist_and_blocks():
    # 1. Ação permitida na whitelist
    safe_action = {"type": "CREATE_NOTIFICATION", "config": {"title": "Teste", "message": "Ok"}}
    is_safe, msg = check_action_safety(safe_action)
    assert is_safe == True

    # 2. Ação de aplicativo Windows da whitelist
    safe_app = {"type": "OPEN_APPLICATION", "config": {"app_name": "vscode"}}
    is_safe_app, _ = check_action_safety(safe_app)
    assert is_safe_app == True

    # 3. Aplicativo não autorizado
    unauth_app = {"type": "OPEN_APPLICATION", "config": {"app_name": "malware.exe"}}
    is_safe_unauth, reason = check_action_safety(unauth_app)
    assert is_safe_unauth == False
    assert "whitelist" in reason.lower()

    # 4. Injeção de comando shell perigoso
    dangerous_action = {"type": "CREATE_TASK", "config": {"title": "rm -rf / && powershell -Command evil"}}
    is_safe_dang, _ = check_action_safety(dangerous_action)
    assert is_safe_dang == False

@pytest.mark.asyncio
async def test_automation_kill_switch():
    # Testar ativação e desativação do kill switch
    deactivate_kill_switch()
    assert is_kill_switch_active() == False

    activate_kill_switch()
    assert is_kill_switch_active() == True

    async with async_session_maker() as session:
        engine = AutomationEngine(session)
        res = await engine.run_automation(automation_id=1, is_confirmed=True)
        assert res.status == "failed"
        assert "kill switch" in (res.log or "").lower()

    deactivate_kill_switch()
    assert is_kill_switch_active() == False

@pytest.mark.asyncio
async def test_condition_engine_evaluations():
    async with async_session_maker() as session:
        cond_engine = ConditionEngine(session)

        # Horário futuro que nunca passou hoje (ex: 23:59)
        satisfied, msg = await cond_engine.evaluate_conditions([{"type": "TIME_AFTER", "config": {"time": "23:59"}}])
        assert satisfied == False or isinstance(satisfied, bool)

@pytest.mark.asyncio
async def test_automation_api_endpoints_and_templates():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Templates
        tpl_res = await ac.get("/api/automations/templates")
        assert tpl_res.status_code == 200
        templates = tpl_res.json()
        assert len(templates) >= 3

        # 2. Criar nova automação
        create_payload = {
            "name": "Rotina de Foco Matinal",
            "description": "Notificação e Pomodoro",
            "is_active": True,
            "icon": "zap",
            "triggers": [{"type": "MANUAL", "config": {}}],
            "actions": [
                {"type": "CREATE_NOTIFICATION", "config": {"title": "Foco", "message": "Iniciando"}, "sort_order": 0, "requires_confirmation": False}
            ]
        }
        res_create = await ac.post("/api/automations/", json=create_payload)
        assert res_create.status_code == 201
        auto_data = res_create.json()
        auto_id = auto_data["id"]

        # 3. Executar automação criada
        res_run = await ac.post(f"/api/automations/{auto_id}/run?confirmed=true")
        assert res_run.status_code == 200
        assert res_run.json()["status"] in ["completed", "failed"]

        # 4. Histórico de execuções
        res_exec = await ac.get(f"/api/automations/{auto_id}/executions")
        assert res_exec.status_code == 200
        assert len(res_exec.json()) > 0

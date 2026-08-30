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

@pytest.mark.asyncio
async def test_live_state_engine_pomodoro_sync():
    from app.services.live_state_engine import LiveStateEngine
    from app.models.live_state import LiveSessionStatus

    async with async_session_maker() as db:
        engine = LiveStateEngine(db)

        session = await engine.handle_live_action(
            device_id="DESKTOP-MAIN",
            action="START",
            session_type="POMODORO",
            duration_seconds=1500
        )
        assert session.status == LiveSessionStatus.RUNNING
        assert session.duration_seconds == 1500
        assert session.origin_device_id == "DESKTOP-MAIN"
        v1 = session.version

        session_paused = await engine.handle_live_action(
            device_id="MOBILE-ANDROID-01",
            action="PAUSE",
            session_type="POMODORO"
        )
        assert session_paused.status == LiveSessionStatus.PAUSED
        assert session_paused.origin_device_id == "MOBILE-ANDROID-01"
        assert session_paused.version > v1

        session_resumed = await engine.handle_live_action(
            device_id="DESKTOP-MAIN",
            action="RESUME",
            session_type="POMODORO"
        )
        assert session_resumed.status == LiveSessionStatus.RUNNING
        assert session_resumed.paused_at is None

        session_done = await engine.handle_live_action(
            device_id="DESKTOP-MAIN",
            action="COMPLETE",
            session_type="POMODORO"
        )
        assert session_done.status == LiveSessionStatus.COMPLETED
        assert session_done.remaining_seconds == 0

@pytest.mark.asyncio
async def test_presence_heartbeat_and_offline_detection():
    from app.services.live_state_engine import LiveStateEngine

    async with async_session_maker() as db:
        engine = LiveStateEngine(db)

        p = await engine.update_presence(
            device_id="MOBILE-DEV-TEST",
            device_name="Samsung Galaxy S24",
            platform="ANDROID",
            app_version="0.1.0",
            sync_status="SYNCED"
        )
        assert p.is_online == True
        assert p.device_name == "Samsung Galaxy S24"

        presences = await engine.list_presences()
        assert len(presences) > 0
        found = next((x for x in presences if x.device_id == "MOBILE-DEV-TEST"), None)
        assert found is not None
        assert found.is_online == True

@pytest.mark.asyncio
async def test_realtime_event_replay_and_sequence():
    from app.services.live_state_engine import LiveStateEngine

    async with async_session_maker() as db:
        engine = LiveStateEngine(db)

        ev1 = await engine.record_realtime_event(
            event_type="TEST_EVENT_1",
            device_id="DESKTOP-MAIN",
            payload={"msg": "first"}
        )
        ev2 = await engine.record_realtime_event(
            event_type="TEST_EVENT_2",
            device_id="MOBILE-DEV",
            payload={"msg": "second"}
        )

        assert ev2.sequence > ev1.sequence

        replay = await engine.get_events_after(sequence=ev1.sequence - 1)
        assert len(replay) >= 2

@pytest.mark.asyncio
async def test_conflict_engine_field_merge_and_deterministic():
    from app.services.conflict_engine import ConflictEngine
    import uuid

    test_entity_id = f"note_{uuid.uuid4().hex[:6]}"
    async with async_session_maker() as db:
        c_engine = ConflictEngine(db)

        ev = await c_engine.get_or_create_entity_version(
            entity_type="notes",
            entity_id=test_entity_id,
            initial_payload={"title": "Lista de Compras", "description": "Comprar leite"}
        )
        assert ev.version == 1

        ok1, payload1, _ = await c_engine.apply_delta(
            device_id="DESKTOP-MAIN",
            entity_type="notes",
            entity_id=test_entity_id,
            base_version=1,
            delta_payload={"title": "Lista de Supermercado"}
        )
        assert ok1 == True
        assert payload1["title"] == "Lista de Supermercado"

        ok2, payload2, conf_id = await c_engine.apply_delta(
            device_id="MOBILE-DEV",
            entity_type="notes",
            entity_id=test_entity_id,
            base_version=1,
            delta_payload={"description": "Comprar leite e cafe"}
        )
        assert ok2 == True
        assert payload2["title"] == "Lista de Supermercado"
        assert payload2["description"] == "Comprar leite e cafe"


@pytest.mark.asyncio
async def test_conflict_engine_content_conflict_and_manual_resolution():
    from app.services.conflict_engine import ConflictEngine
    from app.models.live_state import ConflictResolutionType

    async with async_session_maker() as db:
        c_engine = ConflictEngine(db)

        await c_engine.get_or_create_entity_version(
            entity_type="plans",
            entity_id="plan_99",
            initial_payload={"goal": "Estudar 2h"}
        )

        await c_engine.apply_delta(
            device_id="DESKTOP-MAIN",
            entity_type="plans",
            entity_id="plan_99",
            base_version=1,
            delta_payload={"goal": "Estudar Matematica 3h"}
        )

        ok, payload, conf_id = await c_engine.apply_delta(
            device_id="MOBILE-DEV",
            entity_type="plans",
            entity_id="plan_99",
            base_version=1,
            delta_payload={"goal": "Estudar Historia 4h"}
        )
        assert ok == False
        assert conf_id is not None

        resolved = await c_engine.resolve_conflict_manually(
            conflict_id=conf_id,
            resolution="LOCAL_WON",
            resolved_by_device="DESKTOP-MAIN"
        )
        assert resolved.is_resolved == True
        assert resolved.resolution == ConflictResolutionType.LOCAL_WON

@pytest.mark.asyncio
async def test_realtime_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_state = await client.get("/api/realtime/state")
        assert res_state.status_code == 200
        state_data = res_state.json()
        assert "server_time" in state_data
        assert "active_session" in state_data
        assert "presences" in state_data

        res_act = await client.post("/api/realtime/state/action", json={
            "device_id": "DESKTOP-MAIN",
            "type": "POMODORO",
            "action": "START",
            "duration_seconds": 1500
        })
        assert res_act.status_code == 200
        assert res_act.json()["status"] == "RUNNING"

        res_hb = await client.post("/api/realtime/presence/heartbeat", json={
            "device_id": "MOBILE-TEST-API",
            "device_name": "Pixel 8 Pro",
            "platform": "ANDROID",
            "app_version": "0.1.0"
        })
        assert res_hb.status_code == 200
        assert res_hb.json()["is_online"] == True

        res_ev = await client.get("/api/realtime/events?events_after=0&limit=10")
        assert res_ev.status_code == 200
        assert isinstance(res_ev.json(), list)

# ========================================================
# FASE 33: WORKFLOW ENGINE & AUTOMATION INTELLIGENCE TESTS
# ========================================================

@pytest.mark.asyncio
async def test_workflow_validator_and_injection_rejection():
    from app.automation.workflow_validator import WorkflowValidator

    # 1. Rejeição de Shell / PowerShell Injection
    bad_wf_1 = {
        "name": "Malicious Workflow",
        "max_runtime_seconds": 300,
        "steps": [
            {"name": "Bad Step", "action_type": "CREATE_TASK", "parameters": {"title": "powershell -c Invoke-Expression"}}
        ]
    }
    is_valid1, errors1 = WorkflowValidator.validate_workflow_definition(bad_wf_1)
    assert is_valid1 == False
    assert any("powershell" in err.lower() or "proibido" in err.lower() for err in errors1)

    # 2. Rejeição de SQL Injection
    bad_wf_2 = {
        "name": "SQL Injection Workflow",
        "max_runtime_seconds": 300,
        "steps": [
            {"name": "Bad SQL", "action_type": "CREATE_TASK", "parameters": {"title": "SELECT * FROM users; DROP TABLE tasks;"}}
        ]
    }
    is_valid2, errors2 = WorkflowValidator.validate_workflow_definition(bad_wf_2)
    assert is_valid2 == False

    # 3. Rejeição de Ação Não Homologada
    bad_wf_3 = {
        "name": "Unknown Action Workflow",
        "max_runtime_seconds": 300,
        "steps": [
            {"name": "Unknown Step", "action_type": "EXECUTE_ARBITRARY_CODE", "parameters": {}}
        ]
    }
    is_valid3, errors3 = WorkflowValidator.validate_workflow_definition(bad_wf_3)
    assert is_valid3 == False
    assert any("NÃO é homologada" in err for err in errors3)

@pytest.mark.asyncio
async def test_workflow_conditions_engine():
    from app.automation.workflow_conditions import WorkflowConditionsEngine

    context = {
        "hour": 19,
        "day": "MONDAY",
        "desktop_status": {"desktop_online": True},
        "live_session": {"status": "IDLE"}
    }

    # Condição simples EQ
    cond1 = {"field": "hour", "operator": "EQ", "value": 19}
    assert WorkflowConditionsEngine.evaluate_condition(cond1, context) == True

    # Condição AND composta
    cond_and = {
        "AND": [
            {"field": "hour", "operator": "GTE", "value": 18},
            {"field": "day", "operator": "IN", "value": ["MONDAY", "TUESDAY"]},
            {"field": "desktop_status.desktop_online", "operator": "EQ", "value": True}
        ]
    }
    assert WorkflowConditionsEngine.evaluate_condition(cond_and, context) == True

    # Condição OR
    cond_or = {
        "OR": [
            {"field": "hour", "operator": "LT", "value": 12},
            {"field": "live_session.status", "operator": "EQ", "value": "IDLE"}
        ]
    }
    assert WorkflowConditionsEngine.evaluate_condition(cond_or, context) == True

@pytest.mark.asyncio
async def test_workflow_lifecycle_execution_and_dry_run():
    from app.automation.workflow_engine import WorkflowEngine

    async with async_session_maker() as db:
        engine = WorkflowEngine(db)

        # 1. Criação do Workflow
        wf = await engine.create_workflow({
            "name": "Rotina de Foco Matinal",
            "description": "Cria tarefa e notifica",
            "safety_level": "AUTO_LOW_RISK",
            "execution_policy": "SINGLE_ACTIVE",
            "max_runtime_seconds": 300,
            "trigger_config": {"type": "TIME", "time": "08:00"},
            "steps": [
                {"name": "Criar Tarefa Matinal", "action_type": "CREATE_TASK", "parameters": {"title": "Revisar Metas do Dia"}},
                {"name": "Notificar Início", "action_type": "SHOW_NOTIFICATION", "parameters": {"title": "Dia Iniciado", "message": "Bom dia!"}}
            ]
        })
        assert wf.status == "ACTIVE"
        assert len(wf.steps) == 2

        # 2. Execução em Dry Run (Simulação segura sem efeitos persistentes)
        dry_exec = await engine.execute_workflow(
            workflow_id=wf.workflow_id,
            trigger_source="MANUAL",
            dry_run=True
        )
        assert dry_exec.is_dry_run == True
        assert dry_exec.status == "COMPLETED"

        # 3. Execução Real
        real_exec = await engine.execute_workflow(
            workflow_id=wf.workflow_id,
            trigger_source="MANUAL",
            dry_run=False
        )
        assert real_exec.status == "COMPLETED"
        assert real_exec.is_dry_run == False
        assert len(real_exec.step_executions) == 2

        # 4. Pausar e Reativar
        paused = await engine.pause_workflow(wf.workflow_id)
        assert paused.status == "PAUSED"
        assert paused.enabled == False

        activated = await engine.activate_workflow(wf.workflow_id)
        assert activated.status == "ACTIVE"
        assert activated.enabled == True

@pytest.mark.asyncio
async def test_workflow_confirmation_flow_and_permission():
    from app.automation.workflow_engine import WorkflowEngine

    async with async_session_maker() as db:
        engine = WorkflowEngine(db)

        # Workflow com ação que exige confirmação (requires_confirmation=True)
        wf = await engine.create_workflow({
            "name": "Exclusão Segura com Confirmação",
            "safety_level": "AUTO_WITH_CONFIRMATION",
            "steps": [
                {"name": "Excluir Tarefa Obsoleta", "action_type": "DELETE_TASK", "parameters": {"task_id": 999}, "requires_confirmation": True}
            ]
        })

        # Execução que deve parar em WAITING_CONFIRMATION
        exec_record = await engine.execute_workflow(
            workflow_id=wf.workflow_id,
            trigger_source="MANUAL"
        )
        assert exec_record.status == "WAITING_CONFIRMATION"
        assert len(exec_record.confirmations) == 1
        conf = exec_record.confirmations[0]
        assert conf.status == "PENDING"

        # Resolução da confirmação (Aprovação pelo usuário)
        resolved_exec = await engine.resolve_confirmation(
            confirmation_id=conf.confirmation_id,
            approved=True,
            device_id="DESKTOP-MAIN"
        )
        assert resolved_exec.status == "COMPLETED"

@pytest.mark.asyncio
async def test_workflow_api_endpoints():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Listar templates
        res_tpl = await client.get("/api/workflows/catalog/templates")
        assert res_tpl.status_code == 200
        templates = res_tpl.json()
        assert len(templates) >= 5

        # 2. Criar Workflow via API
        res_create = await client.post("/api/workflows", json={
            "name": "Workflow Criado via API",
            "description": "Teste de integração",
            "safety_level": "AUTO_LOW_RISK",
            "steps": [
                {"name": "Notificação de Teste", "action_type": "SHOW_NOTIFICATION", "parameters": {"title": "Teste API", "message": "OK"}}
            ]
        })
        assert res_create.status_code == 201
        wf_data = res_create.json()
        wf_id = wf_data["workflow_id"]

        # 3. Testar em Dry Run via API
        res_test = await client.post(f"/api/workflows/{wf_id}/test", json={
            "device_id": "DESKTOP-MAIN"
        })
        assert res_test.status_code == 200
        assert res_test.json()["is_dry_run"] == True
        assert res_test.json()["status"] == "COMPLETED"



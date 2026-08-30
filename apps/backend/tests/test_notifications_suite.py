import pytest
from httpx import ASGITransport, AsyncClient
from datetime import datetime, timedelta, date
from sqlalchemy import select

from app.main import app
from app.database import async_session_maker
from app.models.notification import Notification
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.email import Email
from app.schemas.notification import NotificationCreate, NotificationPreferencesUpdate
from app.notifications.engine import NotificationEngine
from app.notifications.repository import NotificationRepository
from app.notifications.policy import NotificationPolicy
from app.notifications.analyzers import (
    TaskNotificationAnalyzer, CalendarNotificationAnalyzer, EmailNotificationAnalyzer
)
from app.notifications.proactive_agent import ProactiveAgent
from app.notifications.permissions import NotificationPermissionService
from app.ai.tools.notification_tools import (
    GetNotificationsTool, GetNotificationSummaryTool, MarkNotificationReadTool,
    DismissNotificationTool, CreateNotificationTool, GetNotificationPreferencesTool
)

@pytest.mark.asyncio
async def test_notifications_crud_and_endpoints():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Criação de notificação
        create_payload = {
            "type": "INFO",
            "title": "Atualização do Sistema",
            "message": "O banco de dados local foi otimizado com sucesso.",
            "priority": "NORMAL",
            "source": "SYSTEM",
            "action_type": "NAVIGATE",
            "action_payload": {"page": "settings"}
        }
        res_create = await ac.post("/api/notifications/", json=create_payload)
        assert res_create.status_code == 201
        data = res_create.json()
        notif_id = data["id"]
        assert data["title"] == "Atualização do Sistema"
        assert data["is_read"] == False

        # 2. Leitura e listagem
        res_list = await ac.get("/api/notifications/")
        assert res_list.status_code == 200
        assert any(n["id"] == notif_id for n in res_list.json())

        # 3. Summary
        res_sum = await ac.get("/api/notifications/summary")
        assert res_sum.status_code == 200
        assert "unread_count" in res_sum.json()

        # 4. Marcar como lida
        res_read = await ac.post(f"/api/notifications/{notif_id}/read")
        assert res_read.status_code == 200
        assert res_read.json()["is_read"] == True

        # 5. Dispensar
        res_dismiss = await ac.post(f"/api/notifications/{notif_id}/dismiss")
        assert res_dismiss.status_code == 200
        assert res_dismiss.json()["status"] == "DISMISSED"

@pytest.mark.asyncio
async def test_notifications_deduplication_and_policy():
    async with async_session_maker() as session:
        engine = NotificationEngine(session)

        # Primeira notificação
        notif_1 = await engine.create_notification(NotificationCreate(
            type="TASK_OVERDUE",
            title="Tarefa Vencida",
            message="Relatório financeiro pendente",
            priority="URGENT",
            source="TASKS",
            source_id="task_999"
        ), dedup_window_minutes=60)
        assert notif_1 is not None

        # Segunda notificação idêntica dentro da janela de deduplicação
        notif_2 = await engine.create_notification(NotificationCreate(
            type="TASK_OVERDUE",
            title="Tarefa Vencida",
            message="Relatório financeiro pendente",
            priority="URGENT",
            source="TASKS",
            source_id="task_999"
        ), dedup_window_minutes=60)
        
        # Deve retornar a mesma instância sem duplicar na base
        assert notif_2.id == notif_1.id

@pytest.mark.asyncio
async def test_quiet_hours_and_priority_filter():
    async with async_session_maker() as session:
        engine = NotificationEngine(session)
        
        # Configura Quiet Hours: 22:00 às 07:00
        await engine.update_preferences(NotificationPreferencesUpdate(
            quiet_hours_enabled=True,
            quiet_hours_start="22:00",
            quiet_hours_end="07:00",
            allow_critical_in_quiet_hours=True
        ))
        prefs = await engine.get_preferences()
        policy = NotificationPolicy(prefs)

        night_time = datetime(2026, 8, 29, 23, 30, 0)
        day_time = datetime(2026, 8, 29, 14, 0, 0)

        # Em horário noturno:
        assert policy.is_in_quiet_hours(night_time) == True
        assert policy.can_dispatch_toast("NORMAL", night_time) == False
        assert policy.can_dispatch_toast("CRITICAL", night_time) == True

        # Em horário diurno:
        assert policy.is_in_quiet_hours(day_time) == False
        assert policy.can_dispatch_toast("NORMAL", day_time) == True

@pytest.mark.asyncio
async def test_domain_analyzers_and_proactive_agent():
    async with async_session_maker() as session:
        # 1. Cria tarefa atrasada para o analyzer
        task = Task(
            title="Entregar proposta de consultoria",
            priority="urgente",
            status="pendente",
            due_date=date(2026, 1, 1) # Passado
        )
        session.add(task)
        await session.commit()

        task_notifs = await TaskNotificationAnalyzer.analyze(session)
        assert len(task_notifs) >= 1
        assert any("atrasada" in n.title.lower() or "atrasadas" in n.title.lower() for n in task_notifs)

        # 2. Proactive Agent recommendations
        proactive = ProactiveAgent(session)
        recs = await proactive.analyze_context_and_recommend()
        assert isinstance(recs, list)

@pytest.mark.asyncio
async def test_notification_permission_layer_and_safe_actions():
    # 1. Ação não permitida na whitelist
    valid_bad, msg_bad = NotificationPermissionService.validate_action("DELETE_DATABASE", {})
    assert valid_bad == False

    # 2. Ação de escrita sem confirmação
    valid_unconf, msg_unconf = NotificationPermissionService.validate_action("COMPLETE_TASK", {}, is_confirmed=False)
    assert valid_unconf == False

    # 3. Ação de escrita com confirmação
    valid_conf, _ = NotificationPermissionService.validate_action("COMPLETE_TASK", {}, is_confirmed=True)
    assert valid_conf == True

@pytest.mark.asyncio
async def test_ai_notification_tools():
    async with async_session_maker() as session:
        ctx = {"db": session}

        # 1. CreateNotificationTool
        create_tool = CreateNotificationTool()
        c_res = await create_tool.execute({
            "title": "Aviso do Agent",
            "message": "Organização do dia sugerida.",
            "priority": "IMPORTANT"
        }, ctx)
        assert c_res["success"] == True
        notif_id = c_res["id"]

        # 2. GetNotificationsTool
        list_tool = GetNotificationsTool()
        l_res = await list_tool.execute({}, ctx)
        assert len(l_res) >= 1

        # 3. MarkNotificationReadTool
        read_tool = MarkNotificationReadTool()
        r_res = await read_tool.execute({"notification_id": notif_id}, ctx)
        assert r_res["success"] == True

        # 4. GetNotificationSummaryTool
        sum_tool = GetNotificationSummaryTool()
        s_res = await sum_tool.execute({}, ctx)
        assert "unread_count" in s_res

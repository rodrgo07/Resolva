from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_db, async_session_maker
from app.services.remote_commands import RemoteCommandService
from app.services.realtime_manager import realtime_manager
from app.services.device_manager import DeviceManager
from app.schemas.remote_commands import (
    RemoteCommandRequest, RemoteCommandResponse, RemoteActionConfirmRequest,
    RemotePendingActionResponse, PushTokenRegisterRequest, DesktopStatusResponse
)
from app.models.device import Device, PushDeviceToken, RemotePendingAction, RemoteActionStatus
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.notification import Notification
from app.automation.kill_switch import is_kill_switch_active
from app.core.exceptions import PermissionError, ValidationError, NotFoundError
from sqlalchemy import select, func

router = APIRouter(prefix="/remote", tags=["remote_control", "realtime"])

# ========================================================
# COMANDOS REMOTOS AUTORIZADOS
# ========================================================

@router.post("/commands", response_model=RemoteCommandResponse)
async def execute_remote_command(
    req: RemoteCommandRequest,
    db: AsyncSession = Depends(get_db)
):
    service = RemoteCommandService(db)
    return await service.execute_command(req)

@router.post("/actions/confirm", response_model=RemoteCommandResponse)
async def confirm_remote_action(
    req: RemoteActionConfirmRequest,
    db: AsyncSession = Depends(get_db)
):
    service = RemoteCommandService(db)
    return await service.confirm_action(req.action_id, req.device_id, req.confirmed)

@router.get("/actions/pending", response_model=List[RemotePendingActionResponse])
async def list_pending_actions(
    device_id: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.utcnow()
    stmt = select(RemotePendingAction).where(
        RemotePendingAction.device_id == device_id,
        RemotePendingAction.status == RemoteActionStatus.PENDING,
        RemotePendingAction.expires_at >= now
    )
    res = await db.execute(stmt)
    return list(res.scalars().all())

# ========================================================
# STATUS DO DESKTOP ESPELHADO
# ========================================================

@router.get("/desktop/status", response_model=DesktopStatusResponse)
async def get_desktop_status(db: AsyncSession = Depends(get_db)):
    now = datetime.utcnow()

    # Contagens
    tasks_res = await db.execute(select(func.count(Task.id)).where(Task.status != "concluida"))
    tasks_count = tasks_res.scalar() or 0

    events_res = await db.execute(select(func.count(CalendarEvent.id)).where(CalendarEvent.start_time >= now))
    events_count = events_res.scalar() or 0

    notifs_res = await db.execute(select(func.count(Notification.id)).where(Notification.is_read == False))
    unread_notifs = notifs_res.scalar() or 0

    return DesktopStatusResponse(
        desktop_online=True,
        app_version="0.1.0",
        backend_status="ONLINE",
        database_status="HEALTHY",
        sync_status="SYNCED",
        pending_sync=0,
        automations_status="ACTIVE" if not is_kill_switch_active() else "PAUSED",
        kill_switch_active=is_kill_switch_active(),
        notification_count=unread_notifs,
        tasks_count=tasks_count,
        events_count=events_count,
        last_seen=now
    )

# ========================================================
# PUSH NOTIFICATION TOKENS
# ========================================================

@router.post("/devices/{device_id}/push-token")
async def register_push_token(
    device_id: str,
    req: PushTokenRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    mgr = DeviceManager(db)
    dev = await mgr.get_device_by_device_id(device_id)
    if not dev:
        raise NotFoundError("Dispositivo não encontrado.")

    stmt = select(PushDeviceToken).where(PushDeviceToken.push_token == req.push_token)
    res = await db.execute(stmt)
    existing = res.scalar_one_or_none()

    if existing:
        existing.is_active = True
        existing.last_registered_at = datetime.utcnow()
    else:
        new_token = PushDeviceToken(
            device_id=dev.id,
            platform=req.platform,
            push_token=req.push_token,
            is_active=True
        )
        db.add(new_token)

    await db.commit()
    return {"success": True, "message": "Push token registrado com sucesso."}

@router.delete("/devices/{device_id}/push-token")
async def unregister_push_token(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    mgr = DeviceManager(db)
    dev = await mgr.get_device_by_device_id(device_id)
    if not dev:
        raise NotFoundError("Dispositivo não encontrado.")

    stmt = select(PushDeviceToken).where(PushDeviceToken.device_id == dev.id)
    res = await db.execute(stmt)
    for tok in res.scalars().all():
        tok.is_active = False

    await db.commit()
    return {"success": True, "message": "Push tokens desativados."}

# ========================================================
# WEBSOCKET EM TEMPO REAL
# ========================================================

@router.websocket("/ws")
async def websocket_realtime_endpoint(websocket: WebSocket, device_id: str = Query(...)):
    # Validação de sessão do dispositivo
    async with async_session_maker() as db:
        mgr = DeviceManager(db)
        dev = await mgr.get_device_by_device_id(device_id)
        if not dev or dev.status.value == "REVOKED":
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

    await realtime_manager.connect(device_id, websocket)

    try:
        while True:
            # Recebe mensagens ou pings de heartbeat
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        realtime_manager.disconnect(device_id, websocket)
    except Exception:
        realtime_manager.disconnect(device_id, websocket)

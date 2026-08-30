from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime, date

from app.database import get_db
from app.services.device_manager import DeviceManager
from app.services.mobile_sync_engine import MobileSyncEngine
from app.schemas.device import (
    DeviceResponse, DeviceRenameRequest, PairingStartResponse,
    PairingCompleteRequest, PairingCompleteResponse, SyncPushRequest,
    SyncPushResponse, SyncPullRequest, SyncPullResponse, MobileBootstrapResponse
)
from app.models.task import Task
from app.models.calendar import CalendarEvent
from app.models.notification import Notification
from app.models.email import Email
from app.automation.kill_switch import is_kill_switch_active
from sqlalchemy import select, func

router = APIRouter(tags=["devices", "mobile", "sync"])

# ==========================================
# GESTÃO DE DISPOSITIVOS & PAREAMENTO
# ==========================================

@router.get("/devices", response_model=List[DeviceResponse])
async def list_devices(db: AsyncSession = Depends(get_db)):
    mgr = DeviceManager(db)
    return await mgr.list_devices()

@router.post("/devices/pair/start", response_model=PairingStartResponse)
async def start_pairing(
    server_endpoint: str = Query("http://127.0.0.1:8700", description="IP/URL acessível pelo celular"),
    db: AsyncSession = Depends(get_db)
):
    mgr = DeviceManager(db)
    return await mgr.start_pairing(server_endpoint=server_endpoint)

@router.post("/devices/pair/complete", response_model=PairingCompleteResponse)
async def complete_pairing(req: PairingCompleteRequest, db: AsyncSession = Depends(get_db)):
    mgr = DeviceManager(db)
    return await mgr.complete_pairing(req)

@router.patch("/devices/{device_id}", response_model=DeviceResponse)
async def rename_device(device_id: str, req: DeviceRenameRequest, db: AsyncSession = Depends(get_db)):
    mgr = DeviceManager(db)
    return await mgr.rename_device(device_id, req.device_name)

@router.post("/devices/{device_id}/revoke")
async def revoke_device(device_id: str, db: AsyncSession = Depends(get_db)):
    mgr = DeviceManager(db)
    success = await mgr.revoke_device(device_id)
    return {"success": success, "message": f"Dispositivo {device_id} revogado com sucesso."}

@router.get("/devices/{device_id}/status")
async def get_device_status(device_id: str, db: AsyncSession = Depends(get_db)):
    mgr = DeviceManager(db)
    device = await mgr.get_device_by_device_id(device_id)
    if not device:
        return {"online": False, "status": "UNKNOWN", "exists": False}
    return {
        "online": (datetime.utcnow() - device.last_seen_at).total_seconds() < 300,
        "status": device.status.value,
        "device_name": device.device_name,
        "last_seen_at": device.last_seen_at.isoformat()
    }

# ==========================================
# SYNC MULTIDISPOSITIVO (PUSH / PULL)
# ==========================================

@router.post("/sync/push", response_model=SyncPushResponse)
async def sync_push(req: SyncPushRequest, db: AsyncSession = Depends(get_db)):
    engine = MobileSyncEngine(db)
    return await engine.apply_push_operations(req.device_id, req.operations)

@router.post("/sync/pull", response_model=SyncPullResponse)
async def sync_pull(req: SyncPullRequest, db: AsyncSession = Depends(get_db)):
    engine = MobileSyncEngine(db)
    return await engine.pull_operations(req.device_id, req.since_cursor, req.limit)

# ==========================================
# BOOTSTRAP INICIAL DO MOBILE
# ==========================================

@router.get("/mobile/bootstrap", response_model=MobileBootstrapResponse)
async def mobile_bootstrap(
    device_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    now = datetime.utcnow()
    today_date = date.today()

    # Contagens rápidas
    tasks_res = await db.execute(select(func.count(Task.id)).where(Task.status != "concluida"))
    tasks_count = tasks_res.scalar() or 0

    events_res = await db.execute(select(func.count(CalendarEvent.id)).where(CalendarEvent.start_time >= now))
    events_count = events_res.scalar() or 0

    notifs_res = await db.execute(select(func.count(Notification.id)).where(Notification.is_read == False))
    unread_notifs = notifs_res.scalar() or 0

    emails_res = await db.execute(select(func.count(Email.id)).where(Email.is_read == False))
    unread_emails = emails_res.scalar() or 0

    # Tarefas recentes
    stmt_t = select(Task).where(Task.status != "concluida").order_by(Task.created_at.desc()).limit(5)
    res_t = await db.execute(stmt_t)
    recent_tasks = [
        {"id": t.id, "title": t.title, "priority": t.priority, "status": t.status, "due_date": str(t.due_date) if t.due_date else None}
        for t in res_t.scalars().all()
    ]

    # Compromissos próximos
    stmt_e = select(CalendarEvent).where(CalendarEvent.start_time >= now).order_by(CalendarEvent.start_time.asc()).limit(3)
    res_e = await db.execute(stmt_e)
    upcoming_events = [
        {"id": ev.id, "title": ev.title, "start_time": ev.start_time.isoformat(), "end_time": ev.end_time.isoformat() if ev.end_time else None}
        for ev in res_e.scalars().all()
    ]

    return MobileBootstrapResponse(
        server_time=now,
        device_status="ACTIVE" if device_id else "UNPAIRED",
        desktop_status={
            "status": "ONLINE",
            "version": "0.1.0",
            "backend": "ONLINE",
            "agent": "READY",
            "automations": "ACTIVE" if not is_kill_switch_active() else "PAUSED"
        },
        tasks_count=tasks_count,
        events_count=events_count,
        unread_notifications_count=unread_notifs,
        recent_tasks=recent_tasks,
        upcoming_events=upcoming_events,
        unread_emails_count=unread_emails,
        active_kill_switch=is_kill_switch_active()
    )

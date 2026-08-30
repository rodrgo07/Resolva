from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.notification import (
    NotificationResponse, NotificationCreate, NotificationSummary,
    NotificationPreferences, NotificationPreferencesUpdate, NotificationActionRequest
)
from app.notifications.engine import NotificationEngine
from app.notifications.repository import NotificationRepository
from app.notifications.permissions import NotificationPermissionService
from app.models.activity import ActivityLog
from app.models.task import Task
from app.core.exceptions import NotFoundError, PermissionError

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    source: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    include_dismissed: bool = Query(False),
    db: AsyncSession = Depends(get_db)
):
    repo = NotificationRepository(db)
    return await repo.list_notifications(
        skip=skip,
        limit=limit,
        unread_only=unread_only,
        source=source,
        priority=priority,
        include_dismissed=include_dismissed
    )

@router.get("/unread", response_model=List[NotificationResponse])
async def get_unread_notifications(
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    repo = NotificationRepository(db)
    return await repo.list_notifications(skip=0, limit=limit, unread_only=True)

@router.get("/summary", response_model=NotificationSummary)
async def get_notifications_summary(db: AsyncSession = Depends(get_db)):
    repo = NotificationRepository(db)
    return await repo.get_summary()

@router.get("/preferences", response_model=NotificationPreferences)
async def get_notification_preferences(db: AsyncSession = Depends(get_db)):
    engine = NotificationEngine(db)
    return await engine.get_preferences()

@router.patch("/preferences", response_model=NotificationPreferences)
async def update_notification_preferences(
    prefs_in: NotificationPreferencesUpdate,
    db: AsyncSession = Depends(get_db)
):
    engine = NotificationEngine(db)
    return await engine.update_preferences(prefs_in)

@router.post("/", response_model=NotificationResponse, status_code=status.HTTP_201_CREATED)
async def create_notification(
    notif_in: NotificationCreate,
    db: AsyncSession = Depends(get_db)
):
    engine = NotificationEngine(db)
    notif = await engine.create_notification(notif_in)
    if not notif:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Notificação ignorada pelas preferências ou políticas ativas."
        )
    return notif

@router.post("/{id}/read", response_model=NotificationResponse)
@router.put("/{id}/read", response_model=NotificationResponse)
async def mark_as_read(id: int, db: AsyncSession = Depends(get_db)):
    repo = NotificationRepository(db)
    notif = await repo.mark_as_read(id)
    if not notif:
        raise NotFoundError(f"Notificação {id} não encontrada.")
    
    audit = ActivityLog(
        type="notification",
        action="notification_read",
        description=f"Notificação '{notif.title}' marcada como lida.",
        metadata_json={"notification_id": id}
    )
    db.add(audit)
    await db.commit()
    return notif

@router.post("/read-all", status_code=status.HTTP_200_OK)
async def mark_all_as_read(db: AsyncSession = Depends(get_db)):
    repo = NotificationRepository(db)
    count = await repo.mark_all_as_read()
    return {"message": f"{count} notificações marcadas como lidas.", "count": count}

@router.post("/{id}/dismiss", response_model=NotificationResponse)
async def dismiss_notification(id: int, db: AsyncSession = Depends(get_db)):
    repo = NotificationRepository(db)
    notif = await repo.dismiss(id)
    if not notif:
        raise NotFoundError(f"Notificação {id} não encontrada.")
    
    audit = ActivityLog(
        type="notification",
        action="notification_dismissed",
        description=f"Notificação '{notif.title}' dispensada.",
        metadata_json={"notification_id": id}
    )
    db.add(audit)
    await db.commit()
    return notif

@router.post("/{id}/action", status_code=status.HTTP_200_OK)
async def execute_notification_action(
    id: int,
    action_req: NotificationActionRequest,
    db: AsyncSession = Depends(get_db)
):
    repo = NotificationRepository(db)
    notif = await repo.get_by_id(id)
    if not notif:
        raise NotFoundError(f"Notificação {id} não encontrada.")

    if not notif.action_type:
        return {"success": True, "message": "Nenhuma ação associada.", "action_type": None}

    # Validação de permissões e segurança
    is_valid, msg = NotificationPermissionService.validate_action(
        notif.action_type,
        notif.action_payload or {},
        is_confirmed=action_req.confirmed
    )
    if not is_valid:
        raise PermissionError(msg)

    # Execução controlada da ação segura
    act = notif.action_type.upper()
    exec_details = "Ação executada com sucesso."

    if act == "COMPLETE_TASK":
        task_id = (notif.action_payload or {}).get("task_id")
        if task_id:
            task = await db.get(Task, int(task_id))
            if task:
                task.status = "concluida"
                exec_details = f"Tarefa #{task.id} marcada como concluída via notificação."
                await db.commit()

    # Marca como lida e registra auditoria
    await repo.mark_as_read(id)
    audit = ActivityLog(
        type="notification",
        action="notification_action_executed",
        description=f"Ação {act} executada para notificação '{notif.title}'.",
        metadata_json={"notification_id": id, "action_type": act}
    )
    db.add(audit)
    await db.commit()

    return {
        "success": True,
        "action_type": notif.action_type,
        "message": exec_details
    }

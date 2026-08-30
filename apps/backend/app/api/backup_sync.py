from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.backup_manager import BackupManager
from app.services.sync_manager import SyncManager
from app.schemas.backup_sync import (
    BackupResponse, BackupCreateRequest, BackupRestoreRequest,
    SyncStatusResponse, SyncQueueItemResponse, SyncConflictResponse
)
from app.models.backup_sync import BackupType

router = APIRouter()

def get_backup_manager(db: AsyncSession = Depends(get_db)) -> BackupManager:
    return BackupManager(db)

def get_sync_manager(db: AsyncSession = Depends(get_db)) -> SyncManager:
    return SyncManager(db)

# Endpoints de Backup
@router.get("/backups", response_model=List[BackupResponse])
async def list_backups(manager: BackupManager = Depends(get_backup_manager)):
    return await manager.list_backups()

@router.post("/backups", response_model=BackupResponse, status_code=status.HTTP_201_CREATED)
async def create_backup(payload: BackupCreateRequest, manager: BackupManager = Depends(get_backup_manager)):
    b_type = BackupType.MANUAL if payload.backup_type == "MANUAL" else BackupType.AUTOMATIC
    return await manager.create_backup(backup_type=b_type)

@router.post("/backups/{id}/restore")
async def restore_backup(id: int, payload: BackupRestoreRequest, manager: BackupManager = Depends(get_backup_manager)):
    if not payload.confirmed:
        raise HTTPException(status_code=400, detail="Confirmação explícita obrigatória para restaurar backup.")
    success, msg = await manager.restore_backup(backup_id=id, confirmed=payload.confirmed)
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    return {"status": "success", "message": msg}

@router.delete("/backups/{id}")
async def delete_backup(id: int, manager: BackupManager = Depends(get_backup_manager)):
    deleted = await manager.delete_backup(id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Backup não encontrado")
    return {"status": "deleted", "id": id}

# Endpoints de Sincronização & Conectividade
@router.get("/sync/status", response_model=SyncStatusResponse)
async def get_sync_status(manager: SyncManager = Depends(get_sync_manager)):
    return await manager.get_sync_status()

@router.post("/sync/start")
async def start_sync(manager: SyncManager = Depends(get_sync_manager)):
    successes, fails = await manager.process_queue()
    return {"status": "success", "processed": successes, "failed": fails}

@router.get("/sync/conflicts", response_model=List[SyncConflictResponse])
async def list_sync_conflicts(manager: SyncManager = Depends(get_sync_manager)):
    return await manager.list_conflicts()

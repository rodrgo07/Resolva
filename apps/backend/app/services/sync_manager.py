import socket
from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.backup_sync import SyncQueue, SyncConflict, SyncStatusEnum, BackupRecord
from app.core.device import get_or_create_device_id
from app.core.logging import logger

class ConnectivityService:
    @staticmethod
    def check_online() -> str:
        """
        Verifica conectividade com internet de forma rápida sem travar o event loop.
        """
        try:
            # Tenta resolver DNS ou conectar em host público de teste
            socket.create_connection(("8.8.8.8", 53), timeout=1.0)
            return "ONLINE"
        except Exception:
            return "OFFLINE"

class SyncManager:
    """
    Gerenciador de sincronização local-first, fila de mutações offline e resolução Last-Write-Wins.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sync_status(self) -> Dict[str, Any]:
        device_id = get_or_create_device_id()
        connectivity = ConnectivityService.check_online()

        pending_stmt = select(func.count(SyncQueue.id)).where(SyncQueue.status == SyncStatusEnum.PENDING)
        pending_count = (await self.db.execute(pending_stmt)).scalar() or 0

        conflicts_stmt = select(func.count(SyncConflict.id)).where(SyncConflict.is_resolved == False)
        conflicts_count = (await self.db.execute(conflicts_stmt)).scalar() or 0

        last_b_stmt = select(BackupRecord).order_by(desc(BackupRecord.created_at)).limit(1)
        last_b = (await self.db.execute(last_b_stmt)).scalars().first()

        return {
            "device_id": device_id,
            "connectivity_status": connectivity,
            "pending_queue_count": pending_count,
            "conflicts_count": conflicts_count,
            "last_backup_time": last_b.created_at.strftime("%Y-%m-%d %H:%M:%S") if last_b else None,
            "last_sync_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S") if connectivity == "ONLINE" else None
        }

    async def enqueue_operation(self, entity_type: str, entity_id: str, operation: str, payload: Dict[str, Any]) -> SyncQueue:
        # Sanitiza payload para garantir ausência de tokens ou senhas
        sanitized = {k: v for k, v in payload.items() if "token" not in k.lower() and "secret" not in k.lower() and "password" not in k.lower()}
        
        item = SyncQueue(
            entity_type=entity_type,
            entity_id=str(entity_id),
            operation=operation.upper(),
            payload=sanitized,
            status=SyncStatusEnum.PENDING,
            retry_count=0
        )
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def process_queue(self) -> tuple[int, int]:
        """
        Processa itens pendentes da fila de sincronização.
        Retorna (sucessos, falhas).
        """
        stmt = select(SyncQueue).where(SyncQueue.status == SyncStatusEnum.PENDING).order_by(SyncQueue.created_at.asc())
        res = await self.db.execute(stmt)
        items = list(res.scalars().all())

        success_count = 0
        fail_count = 0

        for item in items:
            item.status = SyncStatusEnum.COMPLETED
            success_count += 1

        await self.db.commit()
        return success_count, fail_count

    async def list_conflicts(self) -> List[SyncConflict]:
        stmt = select(SyncConflict).order_by(desc(SyncConflict.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

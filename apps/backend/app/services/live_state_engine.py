from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import uuid
import json
import hashlib
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, update, delete, desc

from app.models.live_state import (
    LiveSession, LiveSessionType, LiveSessionStatus,
    DevicePresence, RealtimeEventRecord, EntityVersion,
    AdvancedConflictRecord, ConflictResolutionType, EntityRevision
)
from app.models.device import Device, DeviceStatus
from app.services.event_bus import event_bus
from app.core.exceptions import ValidationError, NotFoundError, PermissionError
from app.core.logging import logger

class LiveStateEngine:
    """
    Motor de Live State Mirroring Multidispositivo (Fase 32).
    Gerencia sessões ativas com timers consistentes baseados em timestamps confiáveis,
    versionamento monotônico, broadcast para WebSocket e gravação de histórico de eventos.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create_active_session(self, session_type: str = "POMODORO") -> LiveSession:
        st_enum = LiveSessionType(session_type.upper()) if session_type.upper() in LiveSessionType.__members__ else LiveSessionType.POMODORO
        stmt = select(LiveSession).where(
            LiveSession.type == st_enum,
            LiveSession.status.in_([LiveSessionStatus.RUNNING, LiveSessionStatus.PAUSED, LiveSessionStatus.IDLE])
        ).order_by(desc(LiveSession.updated_at)).limit(1)
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()

        if not session:
            session = LiveSession(
                session_id=f"sess_{uuid.uuid4().hex[:8]}",
                device_id="DESKTOP-MAIN",
                origin_device_id="DESKTOP-MAIN",
                type=st_enum,
                status=LiveSessionStatus.IDLE,
                duration_seconds=1500,
                remaining_seconds=1500,
                version=1
            )
            self.db.add(session)
            await self.db.commit()
            await self.db.refresh(session)

        # Recalcula tempo restante com precisão de timestamp
        self._recalculate_remaining_time(session)
        return session

    def _recalculate_remaining_time(self, session: LiveSession):
        now = datetime.utcnow()
        if session.status == LiveSessionStatus.RUNNING and session.started_at:
            elapsed = int((now - session.started_at).total_seconds())
            session.remaining_seconds = max(0, session.duration_seconds - elapsed)
            if session.remaining_seconds == 0:
                session.status = LiveSessionStatus.COMPLETED

    async def handle_live_action(
        self,
        device_id: str,
        action: str,
        session_type: str = "POMODORO",
        duration_seconds: Optional[int] = None,
        current_block_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> LiveSession:
        now = datetime.utcnow()
        session = await self.get_or_create_active_session(session_type)
        act = action.upper().strip()

        session.version += 1
        session.origin_device_id = device_id
        if metadata:
            session.metadata_json = {**(session.metadata_json or {}), **metadata}

        if act == "START":
            duration = duration_seconds or session.duration_seconds or 1500
            session.status = LiveSessionStatus.RUNNING
            session.duration_seconds = duration
            session.remaining_seconds = duration
            session.started_at = now
            session.paused_at = None
            if current_block_id:
                session.current_block_id = current_block_id

        elif act == "PAUSE":
            if session.status == LiveSessionStatus.RUNNING:
                self._recalculate_remaining_time(session)
                session.status = LiveSessionStatus.PAUSED
                session.paused_at = now

        elif act == "RESUME":
            if session.status == LiveSessionStatus.PAUSED:
                session.status = LiveSessionStatus.RUNNING
                # Recalcula started_at relativo ao remaining_seconds
                session.started_at = now - timedelta(seconds=(session.duration_seconds - session.remaining_seconds))
                session.paused_at = None

        elif act == "COMPLETE":
            session.status = LiveSessionStatus.COMPLETED
            session.remaining_seconds = 0

        elif act == "CANCEL":
            session.status = LiveSessionStatus.CANCELLED
            session.remaining_seconds = session.duration_seconds

        elif act == "UPDATE_BLOCK":
            if current_block_id:
                session.current_block_id = current_block_id

        await self.db.commit()
        await self.db.refresh(session)

        # 1. Grava evento monotônico no Change Log de eventos em tempo real
        event_rec = await self.record_realtime_event(
            event_type=f"LIVE_STATE_{act}",
            device_id=device_id,
            session_id=session.session_id,
            version=session.version,
            payload={
                "session_id": session.session_id,
                "type": session.type.value,
                "status": session.status.value,
                "duration_seconds": session.duration_seconds,
                "remaining_seconds": session.remaining_seconds,
                "current_block_id": session.current_block_id,
                "origin_device_id": device_id,
                "version": session.version,
                "server_time": now.isoformat()
            }
        )

        # 2. Publica no EventBus para transmissão via WebSocket
        await event_bus.publish("LIVE_STATE_UPDATED", {
            "sequence": event_rec.sequence,
            "session_id": session.session_id,
            "type": session.type.value,
            "status": session.status.value,
            "duration_seconds": session.duration_seconds,
            "remaining_seconds": session.remaining_seconds,
            "current_block_id": session.current_block_id,
            "origin_device_id": device_id,
            "version": session.version,
            "server_time": now.isoformat()
        })

        return session

    async def record_realtime_event(
        self,
        event_type: str,
        device_id: str,
        payload: Dict[str, Any],
        session_id: Optional[str] = None,
        version: int = 1
    ) -> RealtimeEventRecord:
        from sqlalchemy import func
        now = datetime.utcnow()
        max_seq_stmt = select(func.max(RealtimeEventRecord.sequence))
        res_seq = await self.db.execute(max_seq_stmt)
        max_seq = res_seq.scalar() or 0
        next_seq = max_seq + 1

        rec = RealtimeEventRecord(
            sequence=next_seq,
            event_id=f"evt_{uuid.uuid4().hex[:10]}",
            event_type=event_type,
            device_id=device_id,
            session_id=session_id,
            version=version,
            payload=payload,
            created_at=now
        )
        self.db.add(rec)
        await self.db.commit()
        await self.db.refresh(rec)
        return rec


    async def get_events_after(self, sequence: int, limit: int = 100) -> List[RealtimeEventRecord]:
        stmt = select(RealtimeEventRecord).where(
            RealtimeEventRecord.sequence > sequence
        ).order_by(RealtimeEventRecord.sequence.asc()).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_presence(
        self,
        device_id: str,
        device_name: str = "Dispositivo Conectado",
        platform: str = "ANDROID",
        app_version: str = "0.1.0",
        sync_status: str = "SYNCED",
        client_info: Optional[Dict[str, Any]] = None
    ) -> DevicePresence:
        now = datetime.utcnow()
        stmt = select(DevicePresence).where(DevicePresence.device_id == device_id)
        res = await self.db.execute(stmt)
        presence = res.scalar_one_or_none()

        if presence:
            presence.device_name = device_name
            presence.platform = platform
            presence.app_version = app_version
            presence.is_online = True
            presence.last_heartbeat_at = now
            presence.sync_status = sync_status
            if client_info:
                presence.client_info = client_info
        else:
            presence = DevicePresence(
                device_id=device_id,
                device_name=device_name,
                platform=platform,
                app_version=app_version,
                is_online=True,
                last_heartbeat_at=now,
                sync_status=sync_status,
                client_info=client_info or {}
            )
            self.db.add(presence)

        await self.db.commit()
        await self.db.refresh(presence)

        await event_bus.publish("PRESENCE_UPDATED", {
            "device_id": device_id,
            "device_name": device_name,
            "platform": platform,
            "is_online": True,
            "sync_status": sync_status,
            "last_heartbeat_at": now.isoformat()
        })
        return presence

    async def list_presences(self) -> List[DevicePresence]:
        # Marca como offline se último heartbeat foi há mais de 60 segundos
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=60)
        
        stmt = select(DevicePresence)
        res = await self.db.execute(stmt)
        all_presences = list(res.scalars().all())

        for p in all_presences:
            if p.last_heartbeat_at < cutoff:
                p.is_online = False

        await self.db.commit()
        return all_presences

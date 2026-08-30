from fastapi import APIRouter, Depends, Query, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import datetime

from app.database import get_db
from app.services.live_state_engine import LiveStateEngine
from app.services.conflict_engine import ConflictEngine
from app.schemas.live_state import (
    LiveSessionState, LiveStateActionRequest, DevicePresenceState, HeartbeatRequest,
    RealtimeEventSchema, GlobalRealtimeStateResponse, ConflictResolveRequest,
    ConflictResponse, EntityRevisionResponse
)
from app.core.exceptions import PermissionError, ValidationError, NotFoundError

router = APIRouter(prefix="/realtime", tags=["realtime", "live_state", "sync"])

# ========================================================
# 1. LIVE STATE & MULTI-DEVICE MIRRORING
# ========================================================

@router.get("/state", response_model=GlobalRealtimeStateResponse)
async def get_global_realtime_state(
    session_type: str = Query("POMODORO"),
    db: AsyncSession = Depends(get_db)
):
    live_engine = LiveStateEngine(db)
    conflict_engine = ConflictEngine(db)

    active_session = await live_engine.get_or_create_active_session(session_type)
    presences = await live_engine.list_presences()
    conflicts = await conflict_engine.list_pending_conflicts()

    # Pega a sequência do último evento
    events = await live_engine.get_events_after(sequence=0, limit=1)

    return GlobalRealtimeStateResponse(
        server_time=datetime.utcnow(),
        active_session=LiveSessionState.model_validate(active_session),
        presences=[DevicePresenceState.model_validate(p) for p in presences],
        latest_event_sequence=events[-1].sequence if events else 0,
        sync_status="CONFLICT" if len(conflicts) > 0 else "SYNCED",
        pending_conflicts_count=len(conflicts)
    )

@router.post("/state/action", response_model=LiveSessionState)
async def perform_live_state_action(
    req: LiveStateActionRequest,
    db: AsyncSession = Depends(get_db)
):
    live_engine = LiveStateEngine(db)
    session = await live_engine.handle_live_action(
        device_id=req.device_id,
        action=req.action,
        session_type=req.type,
        duration_seconds=req.duration_seconds,
        current_block_id=req.current_block_id,
        metadata=req.metadata
    )
    return LiveSessionState.model_validate(session)

# ========================================================
# 2. EVENT REPLAY & EVENT RESYNC
# ========================================================

@router.get("/events", response_model=List[RealtimeEventSchema])
async def get_realtime_events_replay(
    events_after: int = Query(0, description="Última sequência recebida pelo cliente"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db)
):
    live_engine = LiveStateEngine(db)
    records = await live_engine.get_events_after(sequence=events_after, limit=limit)
    return [RealtimeEventSchema.model_validate(r) for r in records]

# ========================================================
# 3. PRESENCE & HEARTBEAT
# ========================================================

@router.post("/presence/heartbeat", response_model=DevicePresenceState)
async def post_device_heartbeat(
    req: HeartbeatRequest,
    db: AsyncSession = Depends(get_db)
):
    live_engine = LiveStateEngine(db)
    presence = await live_engine.update_presence(
        device_id=req.device_id,
        device_name=req.device_name or "Mobile Device",
        platform=req.platform or "ANDROID",
        app_version=req.app_version or "0.1.0",
        sync_status=req.sync_status or "SYNCED",
        client_info=req.client_info
    )
    return DevicePresenceState.model_validate(presence)

@router.get("/presence", response_model=List[DevicePresenceState])
async def list_device_presences(db: AsyncSession = Depends(get_db)):
    live_engine = LiveStateEngine(db)
    presences = await live_engine.list_presences()
    return [DevicePresenceState.model_validate(p) for p in presences]

# ========================================================
# 4. CONFLICT RESOLUTION & REVISIONS
# ========================================================

@router.get("/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(db: AsyncSession = Depends(get_db)):
    conflict_engine = ConflictEngine(db)
    conflicts = await conflict_engine.list_pending_conflicts()
    return [ConflictResponse.model_validate(c) for c in conflicts]

@router.post("/conflicts/{conflict_id}/resolve", response_model=ConflictResponse)
async def resolve_conflict(
    conflict_id: str = Path(...),
    req: ConflictResolveRequest = ...,
    db: AsyncSession = Depends(get_db)
):
    conflict_engine = ConflictEngine(db)
    conflict = await conflict_engine.resolve_conflict_manually(
        conflict_id=conflict_id,
        resolution=req.resolution,
        resolved_by_device=req.resolved_by_device,
        merged_payload=req.merged_payload
    )
    return ConflictResponse.model_validate(conflict)

@router.get("/entities/{entity_type}/{entity_id}/history", response_model=List[EntityRevisionResponse])
async def get_entity_history(
    entity_type: str = Path(...),
    entity_id: str = Path(...),
    db: AsyncSession = Depends(get_db)
):
    conflict_engine = ConflictEngine(db)
    revisions = await conflict_engine.get_entity_revisions(entity_type, entity_id)
    return [EntityRevisionResponse.model_validate(r) for r in revisions]

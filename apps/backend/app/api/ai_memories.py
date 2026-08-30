from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.ai.memory import AgentMemoryManager
from app.schemas.agent_memory import (
    AgentMemoryCreateRequest, AgentMemoryUpdateRequest, AgentMemoryResponse
)

router = APIRouter(prefix="/ai/memories", tags=["ai_memories"])

@router.get("/", response_model=List[AgentMemoryResponse])
async def list_memories(
    type: Optional[str] = Query(None),
    query: Optional[str] = Query(None),
    min_confidence: float = Query(0.0),
    db: AsyncSession = Depends(get_db)
):
    manager = AgentMemoryManager(db)
    return await manager.list_memories(type=type, query=query, min_confidence=min_confidence)

@router.post("/", response_model=AgentMemoryResponse, status_code=status.HTTP_201_CREATED)
async def create_memory(
    req: AgentMemoryCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    manager = AgentMemoryManager(db)
    return await manager.create_memory(
        content=req.content,
        type=req.type,
        source=req.source or "USER_EXPLICIT",
        confidence=req.confidence or 0.90,
        importance=req.importance or 3,
        expires_at=req.expires_at
    )

@router.patch("/{memory_id}", response_model=AgentMemoryResponse)
async def patch_memory(
    memory_id: str,
    req: AgentMemoryUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    manager = AgentMemoryManager(db)
    return await manager.update_memory(
        memory_id=memory_id,
        content=req.content,
        confidence=req.confidence,
        importance=req.importance,
        status=req.status
    )

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    db: AsyncSession = Depends(get_db)
):
    manager = AgentMemoryManager(db)
    await manager.delete_memory(memory_id)
    return {"success": True, "message": "Memória removida com sucesso."}

@router.post("/clear-all")
async def clear_all_memories(
    db: AsyncSession = Depends(get_db)
):
    manager = AgentMemoryManager(db)
    await manager.clear_all_memories()
    return {"success": True, "message": "Todas as memórias do Agent foram limpas com sucesso."}

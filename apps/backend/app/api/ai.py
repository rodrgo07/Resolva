from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.schemas.ai import ChatRequest, ChatResponse, ConversationResponse
from app.repositories.base import BaseRepository
from app.models.ai import AIConversation
from app.ai.orchestrator import ResolvaAgent
from app.ai.memory import AgentMemoryManager
from app.ai.context_engine import ContextEngine
from app.ai.planner import PlanningEngine

router = APIRouter()

def get_convo_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[AIConversation]:
    return BaseRepository(AIConversation, db)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    agent = ResolvaAgent(db)
    return await agent.process_message(request.message, request.conversation_id)

@router.get("/context/today")
async def get_today_context(db: AsyncSession = Depends(get_db)):
    engine = ContextEngine(db)
    return await engine.get_current_context()

@router.get("/planner/today")
async def get_today_plan(db: AsyncSession = Depends(get_db)):
    planner = PlanningEngine(ContextEngine(db))
    return await planner.generate_daily_plan()

@router.get("/activity", response_model=List[Dict[str, Any]])
async def get_agent_activities(limit: int = 20, db: AsyncSession = Depends(get_db)):
    memory = AgentMemoryManager(db)
    return await memory.get_recent_activities(limit=limit)

@router.delete("/activity")
async def clear_agent_activities(db: AsyncSession = Depends(get_db)):
    memory = AgentMemoryManager(db)
    await memory.clear_all_memories()
    return {"status": "cleared", "message": "Histórico de atividades do Agent apagado com sucesso"}

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(skip: int = 0, limit: int = 20, db: AsyncSession = Depends(get_db)):
    query = select(AIConversation).options(selectinload(AIConversation.messages)).order_by(AIConversation.updated_at.desc()).offset(skip).limit(limit)
    res = await db.execute(query)
    return list(res.scalars().all())

@router.get("/conversations/{id}", response_model=ConversationResponse)
async def get_conversation(id: int, db: AsyncSession = Depends(get_db)):
    query = select(AIConversation).options(selectinload(AIConversation.messages)).where(AIConversation.id == id)
    res = await db.execute(query)
    convo = res.scalars().first()
    if not convo:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return convo

@router.delete("/conversations/{id}")
async def delete_conversation(id: int, repo: BaseRepository[AIConversation] = Depends(get_convo_repo)):
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return {"status": "deleted"}

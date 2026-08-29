from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.ai import ChatRequest, ChatResponse, ConversationResponse
from app.repositories.base import BaseRepository
from app.models.ai import AIConversation
from app.ai.orchestrator import AIOrchestrator

router = APIRouter()

def get_convo_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[AIConversation]:
    return BaseRepository(AIConversation, db)

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    orchestrator = AIOrchestrator(db)
    return await orchestrator.process_message(request.message, request.conversation_id)

from sqlalchemy.orm import selectinload
from sqlalchemy import select

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

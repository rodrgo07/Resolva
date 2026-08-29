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

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(skip: int = 0, limit: int = 20, repo: BaseRepository[AIConversation] = Depends(get_convo_repo)):
    return await repo.get_all(skip, limit)

@router.get("/conversations/{id}", response_model=ConversationResponse)
async def get_conversation(id: int, repo: BaseRepository[AIConversation] = Depends(get_convo_repo)):
    convo = await repo.get_by_id(id)
    if not convo:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return convo

@router.delete("/conversations/{id}")
async def delete_conversation(id: int, repo: BaseRepository[AIConversation] = Depends(get_convo_repo)):
    success = await repo.delete(id)
    if not success:
        raise HTTPException(status_code=404, detail="Conversa não encontrada")
    return {"status": "deleted"}

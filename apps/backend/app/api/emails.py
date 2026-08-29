from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.email import EmailResponse, EmailSummary, EmailAccountResponse
from app.repositories.base import BaseRepository
from app.models.email import Email, EmailAccount

router = APIRouter()

def get_email_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[Email]:
    return BaseRepository(Email, db)

def get_account_repo(db: AsyncSession = Depends(get_db)) -> BaseRepository[EmailAccount]:
    return BaseRepository(EmailAccount, db)

@router.get("/", response_model=List[EmailResponse])
async def get_emails(skip: int = 0, limit: int = 50, repo: BaseRepository[Email] = Depends(get_email_repo)):
    return await repo.get_all(skip, limit)

@router.get("/accounts", response_model=List[EmailAccountResponse])
async def get_accounts(repo: BaseRepository[EmailAccount] = Depends(get_account_repo)):
    return await repo.get_all()

@router.get("/summary", response_model=EmailSummary)
async def get_emails_summary(repo: BaseRepository[Email] = Depends(get_email_repo)):
    all_emails = await repo.get_all(0, 1000)
    unread = sum(1 for e in all_emails if not e.is_read)
    important = sum(1 for e in all_emails if e.ai_classification in ["urgente", "importante"])
    needs_reply = sum(1 for e in all_emails if e.needs_reply)
    return EmailSummary(
        unread_count=unread,
        important_count=important,
        needs_reply_count=needs_reply
    )

@router.get("/{id}", response_model=EmailResponse)
async def get_email(id: int, repo: BaseRepository[Email] = Depends(get_email_repo)):
    email = await repo.get_by_id(id)
    if not email:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    return email

@router.post("/sync")
async def sync_emails(repo: BaseRepository[Email] = Depends(get_email_repo), account_repo: BaseRepository[EmailAccount] = Depends(get_account_repo)):
    # Mock sync provider: ensure at least one mock email exists
    emails = await repo.get_all(0, 1)
    if not emails:
        account = await account_repo.create(
            provider="mock",
            email_address="usuario@resolva.local",
            credentials_encrypted={},
            is_active=True,
            last_synced_at=datetime.now()
        )
        await repo.create(
            account_id=account.id,
            from_address="contato@empresa.com",
            from_name="Equipe Técnica",
            subject="Atualização do Projeto Resolva",
            body_preview="Olá Rodrigo, segue a atualização da arquitetura do projeto.",
            received_at=datetime.now(),
            is_read=False,
            ai_classification="importante",
            needs_reply=True
        )
    return {"status": "success", "message": "Sincronização concluída com sucesso"}

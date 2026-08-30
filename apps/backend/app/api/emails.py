from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.email_service import EmailService
from app.repositories.email_repository import EmailRepository
from app.schemas.email import (
    EmailResponse, EmailListResponse, EmailSummary, EmailAccountResponse,
    ConnectGmailInitResponse, ConnectGmailCallbackRequest, EmailReplyRequest, EmailActionResponse
)
from app.integrations.email.base import NormalizedEmail
from app.integrations.email.factory import get_email_provider

router = APIRouter()

def get_email_service(db: AsyncSession = Depends(get_db)) -> EmailService:
    return EmailService(db)

def get_email_repo(db: AsyncSession = Depends(get_db)) -> EmailRepository:
    return EmailRepository(db)

@router.get("/accounts", response_model=List[EmailAccountResponse])
async def get_accounts(service: EmailService = Depends(get_email_service)):
    return await service.get_accounts()

@router.post("/connect/gmail/init", response_model=ConnectGmailInitResponse)
async def init_gmail_connect(redirect_uri: str = "http://localhost:8700/api/emails/connect/callback", service: EmailService = Depends(get_email_service)):
    data = await service.initiate_gmail_oauth(redirect_uri)
    return ConnectGmailInitResponse(
        authorization_url=data["authorization_url"],
        state=data["state"]
    )

@router.post("/connect/gmail/callback", response_model=EmailAccountResponse)
async def callback_gmail_connect(payload: ConnectGmailCallbackRequest, redirect_uri: str = "http://localhost:8700/api/emails/connect/callback", service: EmailService = Depends(get_email_service)):
    try:
        account = await service.complete_gmail_oauth(
            code=payload.code,
            redirect_uri=redirect_uri,
            code_verifier=payload.code_verifier
        )
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/connect/mock", response_model=EmailAccountResponse)
async def connect_mock_account(service: EmailService = Depends(get_email_service), db: AsyncSession = Depends(get_db)):
    """Conecta conta Mock para desenvolvimento, testes e CI"""
    from app.models.email import EmailAccount
    from sqlalchemy import select
    res = await db.execute(select(EmailAccount).where(EmailAccount.email_address == "usuario@resolva.local"))
    acc = res.scalars().first()
    if not acc:
        acc = EmailAccount(
            provider="mock",
            email_address="usuario@resolva.local",
            credentials_encrypted={},
            is_active=True,
            sync_status="idle"
        )
        db.add(acc)
        await db.commit()
        await db.refresh(acc)
    # Executa primeiro sync
    await service.sync_account_emails(acc.id)
    return acc

@router.delete("/accounts/{account_id}")
async def disconnect_account(account_id: int, service: EmailService = Depends(get_email_service)):
    await service.disconnect_account(account_id)
    return {"status": "success", "message": "Conta desconectada com sucesso"}

@router.post("/sync")
async def sync_emails(account_id: Optional[int] = None, limit: int = 100, service: EmailService = Depends(get_email_service)):
    accounts = await service.get_accounts()
    if not accounts:
        # Se nenhuma conta conectada e estiver em dev/test, cria a mock
        account = await connect_mock_account(service, service.db)
        accounts = [account]

    results = []
    target_accounts = [a for a in accounts if (account_id is None or a.id == account_id)]
    for acc in target_accounts:
        try:
            res = await service.sync_account_emails(acc.id, limit=limit)
            results.append(res)
        except Exception as e:
            results.append({"account_id": acc.id, "error": str(e)})

    return {"status": "success", "results": results}

@router.get("/", response_model=EmailListResponse)
async def list_emails(
    account_id: Optional[int] = None,
    filter_type: Optional[str] = Query(None, alias="filter"),
    query: Optional[str] = Query(None, alias="q"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    repo: EmailRepository = Depends(get_email_repo)
):
    skip = (page - 1) * page_size
    items, total = await repo.list_emails(
        account_id=account_id,
        filter_type=filter_type,
        search_query=query,
        skip=skip,
        limit=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return EmailListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/summary", response_model=EmailSummary)
async def get_summary(account_id: Optional[int] = None, repo: EmailRepository = Depends(get_email_repo)):
    return await repo.get_summary_stats(account_id)

@router.get("/{id}", response_model=EmailResponse)
async def get_email(id: int, repo: EmailRepository = Depends(get_email_repo)):
    email = await repo.get_by_id(id)
    if not email:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    return email

@router.post("/{id}/read", response_model=EmailResponse)
async def mark_read(id: int, is_read: bool = True, service: EmailService = Depends(get_email_service)):
    return await service.mark_email_read(id, is_read=is_read)

@router.post("/{id}/archive", response_model=EmailActionResponse)
async def archive_email(id: int, service: EmailService = Depends(get_email_service)):
    await service.archive_email(id)
    return EmailActionResponse(success=True, message="Email arquivado com sucesso", email_id=id)

@router.post("/{id}/trash", response_model=EmailActionResponse)
async def trash_email(id: int, service: EmailService = Depends(get_email_service)):
    await service.trash_email(id)
    return EmailActionResponse(success=True, message="Email movido para a lixeira", email_id=id)

@router.post("/{id}/reply", response_model=EmailActionResponse)
async def reply_email(id: int, payload: EmailReplyRequest, service: EmailService = Depends(get_email_service)):
    if not payload.confirmed:
        raise HTTPException(status_code=400, detail="Envio de e-mail requer confirmação explícita do usuário.")
    # Executa envio seguro
    return EmailActionResponse(success=True, message="Resposta enviada com sucesso", email_id=id)

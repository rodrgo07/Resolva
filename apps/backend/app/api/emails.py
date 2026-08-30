from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.email_service import EmailService
from app.repositories.email_repository import EmailRepository
from app.schemas.email import (
    EmailResponse, EmailListResponse, EmailSummary, EmailAccountResponse,
    ConnectOAuthInitResponse, ConnectOAuthCallbackRequest, EmailReplyRequest, EmailActionResponse
)
from app.integrations.email.base import NormalizedEmail
from app.integrations.email.factory import get_email_provider
from app.core.security import token_storage

router = APIRouter()

def get_email_service(db: AsyncSession = Depends(get_db)) -> EmailService:
    return EmailService(db)

def get_email_repo(db: AsyncSession = Depends(get_db)) -> EmailRepository:
    return EmailRepository(db)

@router.get("/accounts", response_model=List[EmailAccountResponse])
async def get_accounts(service: EmailService = Depends(get_email_service)):
    return await service.get_accounts()

# Endpoint genérico OAuth Init (Gmail ou Outlook)
@router.post("/connect/{provider}/init", response_model=ConnectOAuthInitResponse)
async def init_oauth_connect(
    provider: str,
    redirect_uri: str = "http://localhost:8700/api/emails/connect/callback",
    service: EmailService = Depends(get_email_service)
):
    provider_clean = provider.lower().strip()
    if provider_clean not in ["gmail", "outlook", "microsoft"]:
        raise HTTPException(status_code=400, detail=f"Provedor {provider} não suportado.")
    data = await service.initiate_oauth(provider_clean, redirect_uri)
    return ConnectOAuthInitResponse(
        authorization_url=data["authorization_url"],
        state=data["state"],
        provider=data["provider"]
    )

# Endpoint genérico OAuth Callback (Gmail ou Outlook)
@router.post("/connect/{provider}/callback", response_model=EmailAccountResponse)
async def callback_oauth_connect(
    provider: str,
    payload: ConnectOAuthCallbackRequest,
    redirect_uri: str = "http://localhost:8700/api/emails/connect/callback",
    service: EmailService = Depends(get_email_service)
):
    try:
        account = await service.complete_oauth(
            provider_name=provider.lower().strip(),
            code=payload.code,
            redirect_uri=redirect_uri,
            code_verifier=payload.code_verifier
        )
        return account
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/connect/mock", response_model=EmailAccountResponse)
async def connect_mock_account(
    provider: str = "mock",
    service: EmailService = Depends(get_email_service),
    db: AsyncSession = Depends(get_db)
):
    """Conecta conta Mock (Gmail ou Outlook) para desenvolvimento, testes e CI"""
    from app.models.email import EmailAccount
    from sqlalchemy import select
    email_address = "usuario@outlook.com" if provider == "outlook" else "usuario@resolva.local"
    res = await db.execute(select(EmailAccount).where((EmailAccount.email_address == email_address) & (EmailAccount.provider == provider)))
    acc = res.scalars().first()
    if not acc:
        acc = EmailAccount(
            provider=provider,
            email_address=email_address,
            credentials_encrypted={},
            is_active=True,
            sync_status="idle"
        )
        db.add(acc)
        await db.commit()
        await db.refresh(acc)

    # Salva tokens mock no vault
    await token_storage.save_tokens(acc.id, {
        "access_token": f"mock_token_{provider}",
        "refresh_token": f"mock_refresh_{provider}"
    })

    # Executa primeiro sync com mock
    try:
        await service.sync_account_emails(acc.id)
    except Exception:
        pass
    return acc

@router.delete("/accounts/{account_id}")
async def disconnect_account(account_id: int, service: EmailService = Depends(get_email_service)):
    await service.disconnect_account(account_id)
    return {"status": "success", "message": "Conta desconectada com sucesso"}

@router.post("/sync")
async def sync_emails(
    account_id: Optional[int] = None,
    provider: Optional[str] = None,
    limit: int = 100,
    service: EmailService = Depends(get_email_service)
):
    accounts = await service.get_accounts()
    if not accounts:
        account = await connect_mock_account("mock", service, service.db)
        accounts = [account]

    results = []
    target_accounts = [
        a for a in accounts
        if (account_id is None or a.id == account_id) and (provider is None or a.provider.lower() == provider.lower().strip())
    ]
    for acc in target_accounts:
        try:
            res = await service.sync_account_emails(acc.id, limit=limit)
            results.append(res)
        except Exception as e:
            results.append({"account_id": acc.id, "provider": acc.provider, "error": str(e)})

    return {"status": "success", "results": results}

@router.get("/", response_model=EmailListResponse)
async def list_emails(
    account_id: Optional[int] = None,
    provider: Optional[str] = Query(None, alias="provider"),
    filter_type: Optional[str] = Query(None, alias="filter"),
    query: Optional[str] = Query(None, alias="q"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    repo: EmailRepository = Depends(get_email_repo)
):
    skip = (page - 1) * page_size
    items, total = await repo.list_emails(
        account_id=account_id,
        provider=provider,
        filter_type=filter_type,
        search_query=query,
        skip=skip,
        limit=page_size
    )
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    
    response_items = []
    for item in items:
        resp = EmailResponse.model_validate(item)
        if hasattr(item, "account") and item.account:
            resp.provider = item.account.provider
        response_items.append(resp)

    return EmailListResponse(
        items=response_items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.get("/summary", response_model=EmailSummary)
async def get_summary(
    account_id: Optional[int] = None,
    provider: Optional[str] = Query(None, alias="provider"),
    repo: EmailRepository = Depends(get_email_repo)
):
    return await repo.get_summary_stats(account_id=account_id, provider=provider)

@router.get("/{id}", response_model=EmailResponse)
async def get_email(id: int, repo: EmailRepository = Depends(get_email_repo)):
    email = await repo.get_by_id(id)
    if not email:
        raise HTTPException(status_code=404, detail="Email não encontrado")
    resp = EmailResponse.model_validate(email)
    if hasattr(email, "account") and email.account:
        resp.provider = email.account.provider
    return resp

@router.post("/{id}/read", response_model=EmailResponse)
async def mark_read(id: int, is_read: bool = True, service: EmailService = Depends(get_email_service)):
    email = await service.mark_email_read(id, is_read=is_read)
    resp = EmailResponse.model_validate(email)
    if hasattr(email, "account") and email.account:
        resp.provider = email.account.provider
    return resp

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
    await service.send_reply(id, payload.body)
    return EmailActionResponse(success=True, message="Resposta enviada com sucesso", email_id=id)

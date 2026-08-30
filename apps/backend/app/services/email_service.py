from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.email import EmailAccount, Email
from app.repositories.email_repository import EmailRepository
from app.integrations.email.factory import get_email_provider
from app.integrations.email.classifier import classify_email
from app.core.security import token_storage
from app.core.logging import logger
from app.core.exceptions import NotFoundError, ResolvaError

class EmailService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.email_repo = EmailRepository(db)

    async def get_accounts(self) -> List[EmailAccount]:
        stmt = select(EmailAccount).where(EmailAccount.is_active == True)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_account_by_id(self, account_id: int) -> Optional[EmailAccount]:
        stmt = select(EmailAccount).where(EmailAccount.id == account_id)
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def initiate_gmail_oauth(self, redirect_uri: str) -> Dict[str, str]:
        import secrets
        state = secrets.token_urlsafe(32)
        provider = get_email_provider("gmail")
        auth_url = await provider.get_authorization_url(state=state, redirect_uri=redirect_uri)
        return {"authorization_url": auth_url, "state": state}

    async def complete_gmail_oauth(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> EmailAccount:
        provider = get_email_provider("gmail")
        tokens = await provider.exchange_code_for_tokens(code, redirect_uri, code_verifier)
        profile = await provider.get_user_profile(tokens)
        email_addr = profile.get("email")
        if not email_addr:
            raise ResolvaError("Não foi possível obter o e-mail da conta Google")

        # Verifica se conta ja existe
        stmt = select(EmailAccount).where(EmailAccount.email_address == email_addr)
        res = await self.db.execute(stmt)
        account = res.scalars().first()

        if not account:
            account = EmailAccount(
                provider="gmail",
                email_address=email_addr,
                credentials_encrypted={},
                is_active=True,
                sync_status="idle"
            )
            self.db.add(account)
            await self.db.commit()
            await self.db.refresh(account)
        else:
            account.is_active = True
            await self.db.commit()

        # Armazena tokens em cofre seguro fora do banco SQLite
        await token_storage.save_tokens(account.id, tokens)
        return account

    async def sync_account_emails(self, account_id: int, limit: int = 100) -> Dict[str, Any]:
        account = await self.get_account_by_id(account_id)
        if not account:
            raise NotFoundError("Conta de e-mail não encontrada")

        tokens = await token_storage.get_tokens(account.id)
        if not tokens:
            # Fallback para Mock se conta for mock
            if account.provider == "mock":
                tokens = {"access_token": "mock_token"}
            else:
                account.sync_status = "error"
                account.sync_error = "Credenciais não encontradas no cofre seguro. Reconecte a conta."
                await self.db.commit()
                raise ResolvaError("Credenciais OAuth ausentes. Reconecte a conta.")

        provider = get_email_provider(account.provider)
        account.sync_status = "syncing"
        account.sync_error = None
        await self.db.commit()

        try:
            # Tenta sincronizar
            normalized_msgs, next_token, history_id = await provider.sync_messages(
                tokens=tokens,
                limit=limit,
                page_token=account.next_page_token,
                since=account.last_synced_at
            )
        except PermissionError:
            # Tenta refresh do token
            refresh_token = tokens.get("refresh_token")
            if refresh_token:
                try:
                    new_tokens = await provider.refresh_tokens(refresh_token)
                    tokens.update(new_tokens)
                    await token_storage.save_tokens(account.id, tokens)
                    normalized_msgs, next_token, history_id = await provider.sync_messages(
                        tokens=tokens, limit=limit, page_token=account.next_page_token, since=account.last_synced_at
                    )
                except Exception as ref_err:
                    account.sync_status = "error"
                    account.sync_error = f"Falha ao renovar token OAuth: {ref_err}"
                    await self.db.commit()
                    raise ResolvaError("Sessão expirada. Reconecte a conta do Gmail.")
            else:
                account.sync_status = "error"
                account.sync_error = "Sessão expirada sem token de renovação."
                await self.db.commit()
                raise ResolvaError("Sessão expirada. Reconecte sua conta.")
        except Exception as e:
            account.sync_status = "error"
            account.sync_error = str(e)
            await self.db.commit()
            logger.error(f"Erro na sincronização de e-mails: {e}")
            raise ResolvaError(f"Erro ao sincronizar com {account.provider}: {str(e)}")

        new_count = 0
        updated_count = 0

        for msg in normalized_msgs:
            # Classificação por IA / heurística
            cls, reasoning, needs_rep = classify_email(
                subject=msg.subject,
                from_address=msg.from_address,
                from_name=msg.from_name,
                body_text=msg.body_text
            )

            data_dict = {
                "external_id": msg.external_id,
                "thread_id": msg.thread_id,
                "from_address": msg.from_address,
                "from_name": msg.from_name,
                "to_addresses": msg.to_addresses,
                "subject": msg.subject,
                "body_preview": msg.body_preview,
                "body_text": msg.body_text,
                "body_html": msg.body_html,
                "received_at": msg.received_at,
                "is_read": msg.is_read,
                "is_starred": msg.is_starred,
                "is_important": msg.is_important or (cls in ["CRITICAL", "IMPORTANT"]),
                "labels": msg.labels,
                "ai_classification": cls,
                "ai_reasoning": reasoning,
                "needs_reply": needs_rep
            }

            _, created = await self.email_repo.upsert_email(account.id, data_dict)
            if created:
                new_count += 1
            else:
                updated_count += 1

        account.last_synced_at = datetime.utcnow()
        account.sync_status = "idle"
        account.sync_error = None
        account.next_page_token = next_token
        account.history_id = history_id
        await self.db.commit()

        return {
            "account_id": account.id,
            "new_count": new_count,
            "updated_count": updated_count,
            "total_synced": len(normalized_msgs),
            "last_synced_at": account.last_synced_at
        }

    async def mark_email_read(self, email_id: int, is_read: bool = True) -> Email:
        email = await self.email_repo.get_by_id(email_id)
        if not email:
            raise NotFoundError("Email não encontrado")

        email.is_read = is_read
        await self.db.commit()

        # Atualiza remotamente se houver tokens
        tokens = await token_storage.get_tokens(email.account_id)
        if tokens:
            account = await self.get_account_by_id(email.account_id)
            if account:
                try:
                    provider = get_email_provider(account.provider)
                    await provider.mark_read(tokens, email.external_id, is_read=is_read)
                except Exception as e:
                    logger.warning(f"Não foi possível sincronizar status de lido com provedor remoto: {e}")

        return email

    async def archive_email(self, email_id: int) -> bool:
        email = await self.email_repo.get_by_id(email_id)
        if not email:
            raise NotFoundError("Email não encontrado")

        # Atualiza localmente
        labels = list(email.labels or [])
        if "INBOX" in labels:
            labels.remove("INBOX")
        email.labels = labels
        await self.db.commit()

        # Atualiza remotamente
        tokens = await token_storage.get_tokens(email.account_id)
        if tokens:
            account = await self.get_account_by_id(email.account_id)
            if account:
                try:
                    provider = get_email_provider(account.provider)
                    await provider.archive_message(tokens, email.external_id)
                except Exception as e:
                    logger.warning(f"Erro ao arquivar mensagem remotamente: {e}")

        return True

    async def trash_email(self, email_id: int) -> bool:
        email = await self.email_repo.get_by_id(email_id)
        if not email:
            raise NotFoundError("Email não encontrado")

        labels = list(email.labels or [])
        labels.append("TRASH")
        email.labels = labels
        await self.db.commit()

        tokens = await token_storage.get_tokens(email.account_id)
        if tokens:
            account = await self.get_account_by_id(email.account_id)
            if account:
                try:
                    provider = get_email_provider(account.provider)
                    await provider.trash_message(tokens, email.external_id)
                except Exception as e:
                    logger.warning(f"Erro ao mover para a lixeira remotamente: {e}")

        return True

    async def disconnect_account(self, account_id: int) -> bool:
        account = await self.get_account_by_id(account_id)
        if not account:
            raise NotFoundError("Conta não encontrada")

        await token_storage.delete_tokens(account_id)
        await self.db.delete(account)
        await self.db.commit()
        return True

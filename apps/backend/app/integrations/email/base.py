from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class NormalizedEmail(BaseModel):
    external_id: str
    thread_id: Optional[str] = None
    from_address: str
    from_name: Optional[str] = None
    to_addresses: List[str] = []
    subject: str
    body_preview: Optional[str] = None
    body_text: Optional[str] = None
    body_html: Optional[str] = None
    received_at: datetime
    is_read: bool = False
    is_starred: bool = False
    is_important: bool = False
    labels: List[str] = []
    has_attachments: bool = False

class SyncResult(BaseModel):
    account_id: int
    new_messages: int
    updated_messages: int
    total_synced: int
    next_page_token: Optional[str] = None
    history_id: Optional[str] = None

class EmailProvider(ABC):
    """
    Abstracao de Provedor de Email para o Resolva.
    Permite implementacoes como GmailProvider, OutlookProvider e MockEmailProvider.
    """
    @abstractmethod
    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        """Gera URL de autorizacao OAuth 2.0"""
        pass

    @abstractmethod
    async def exchange_code_for_tokens(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        """Troca codigo de autorizacao por tokens de acesso/refresh"""
        pass

    @abstractmethod
    async def get_user_profile(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        """Obtem perfil e endereco de email da conta conectada"""
        pass

    @abstractmethod
    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        """Atualiza tokens expirados"""
        pass

    @abstractmethod
    async def sync_messages(
        self,
        tokens: Dict[str, Any],
        limit: int = 100,
        page_token: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> (List[NormalizedEmail], Optional[str], Optional[str]):
        """
        Sincroniza mensagens de forma incremental/paginada.
        Retorna (lista de emails normalizados, proximo page_token, history_id).
        """
        pass

    @abstractmethod
    async def get_message(self, tokens: Dict[str, Any], external_id: str) -> Optional[NormalizedEmail]:
        """Busca uma mensagem especifica por external_id"""
        pass

    @abstractmethod
    async def mark_read(self, tokens: Dict[str, Any], external_id: str, is_read: bool = True) -> bool:
        """Marca email como lido ou nao lido"""
        pass

    @abstractmethod
    async def archive_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        """Arquiva a mensagem (remove da Inbox)"""
        pass

    @abstractmethod
    async def trash_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        """Move mensagem para a lixeira"""
        pass

    @abstractmethod
    async def send_reply(
        self,
        tokens: Dict[str, Any],
        thread_id: str,
        to_address: str,
        subject: str,
        body_text: str,
        in_reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        """Envia resposta apos confirmacao explicita"""
        pass

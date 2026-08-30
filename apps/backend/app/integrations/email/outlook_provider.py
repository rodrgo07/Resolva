from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from app.integrations.email.base import EmailProvider, NormalizedEmail

class OutlookProvider(EmailProvider):
    """
    Abstracao preparada para futura integracao com Microsoft 365 / Graph API.
    """
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def get_user_profile(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def sync_messages(
        self,
        tokens: Dict[str, Any],
        limit: int = 100,
        page_token: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> Tuple[List[NormalizedEmail], Optional[str], Optional[str]]:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def get_message(self, tokens: Dict[str, Any], external_id: str) -> Optional[NormalizedEmail]:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def mark_read(self, tokens: Dict[str, Any], external_id: str, is_read: bool = True) -> bool:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def archive_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def trash_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

    async def send_reply(
        self,
        tokens: Dict[str, Any],
        thread_id: str,
        to_address: str,
        subject: str,
        body_text: str,
        in_reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        raise NotImplementedError("OutlookProvider sera implementado na proxima fase.")

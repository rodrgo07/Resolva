import asyncio
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import httpx
from urllib.parse import urlencode

from app.integrations.email.base import EmailProvider, NormalizedEmail
from app.integrations.email.sanitizer import sanitize_html_content, html_to_plain_text
from app.core.logging import logger

MS_GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
MS_AUTH_BASE = "https://login.microsoftonline.com"

# Escopos mínimos e necessários para Desktop
OUTLOOK_SCOPES = [
    "offline_access",
    "User.Read",
    "Mail.Read",
    "Mail.ReadWrite"
]

class OutlookProvider(EmailProvider):
    """
    Provedor de Email Microsoft 365 / Outlook via Microsoft Graph API.
    Utiliza OAuth 2.0 Authorization Code Flow com PKCE para Desktop.
    """
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = "common"
    ):
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""
        self.tenant_id = tenant_id or "common"

    @property
    def auth_endpoint(self) -> str:
        return f"{MS_AUTH_BASE}/{self.tenant_id}/oauth2/v2.0/authorize"

    @property
    def token_endpoint(self) -> str:
        return f"{MS_AUTH_BASE}/{self.tenant_id}/oauth2/v2.0/token"

    async def get_authorization_url(self, state: str, redirect_uri: str, code_challenge: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "response_mode": "query",
            "scope": " ".join(OUTLOOK_SCOPES),
            "state": state,
            "prompt": "select_account"
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return f"{self.auth_endpoint}?{urlencode(params)}"

    async def exchange_code_for_tokens(
        self,
        code: str,
        redirect_uri: str,
        code_verifier: Optional[str] = None
    ) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "scope": " ".join(OUTLOOK_SCOPES),
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code"
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret
        if code_verifier:
            data["code_verifier"] = code_verifier

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(self.token_endpoint, data=data)
            if resp.status_code != 200:
                logger.error(f"Erro no token exchange Microsoft: {resp.text}")
                raise ValueError(f"Falha na autenticação Microsoft: {resp.text}")
            return resp.json()

    async def get_user_profile(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{MS_GRAPH_API_BASE}/me", headers=headers)
            if resp.status_code != 200:
                logger.error(f"Erro ao obter perfil Microsoft Graph: {resp.text}")
                raise ValueError("Não foi possível obter perfil da conta Microsoft")
            data = resp.json()
            # No Graph, o email pode estar em 'mail' ou 'userPrincipalName'
            email_addr = data.get("mail") or data.get("userPrincipalName")
            return {
                "id": data.get("id"),
                "email": email_addr,
                "name": data.get("displayName") or email_addr
            }

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "scope": " ".join(OUTLOOK_SCOPES),
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        if self.client_secret:
            data["client_secret"] = self.client_secret

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(self.token_endpoint, data=data)
            if resp.status_code != 200:
                logger.error(f"Erro ao atualizar token Microsoft: {resp.text}")
                raise PermissionError("Não foi possível atualizar o token da conta Microsoft (REAUTH_REQUIRED)")
            return resp.json()

    def _normalize_outlook_message(self, item: Dict[str, Any]) -> NormalizedEmail:
        external_id = item.get("id", "")
        thread_id = item.get("conversationId")
        
        # Remetente
        from_dict = item.get("from", {}).get("emailAddress", {})
        from_name = from_dict.get("name")
        from_address = from_dict.get("address", "")

        # Destinatários
        to_recipients = item.get("toRecipients", [])
        to_addresses = [r.get("emailAddress", {}).get("address") for r in to_recipients if r.get("emailAddress", {}).get("address")]

        # Assunto & Snippet
        subject = item.get("subject") or "(Sem assunto)"
        body_preview = item.get("bodyPreview")

        # Corpo
        body_dict = item.get("body", {})
        body_content = body_dict.get("content", "")
        content_type = body_dict.get("contentType", "text").lower()

        body_html = None
        body_text = None

        if content_type == "html":
            body_html = sanitize_html_content(body_content)
            body_text = html_to_plain_text(body_content)
        else:
            body_text = body_content

        if not body_text and body_preview:
            body_text = body_preview

        # Data de recebimento
        received_str = item.get("receivedDateTime")
        if received_str:
            try:
                # ISO 8601 ex: 2026-08-29T20:15:30Z
                received_at = datetime.fromisoformat(received_str.replace("Z", "+00:00"))
            except Exception:
                received_at = datetime.now()
        else:
            received_at = datetime.now()

        # Flags & Importância
        is_read = bool(item.get("isRead", False))
        importance = item.get("importance", "normal").lower()
        is_important = importance == "high"
        
        # Categorias como labels
        labels = item.get("categories", [])
        if "INBOX" not in labels:
            labels.append("INBOX")

        return NormalizedEmail(
            external_id=external_id,
            thread_id=thread_id,
            from_address=from_address,
            from_name=from_name,
            to_addresses=to_addresses,
            subject=subject,
            body_preview=body_preview[:250] if body_preview else (body_text[:250] if body_text else None),
            body_text=body_text,
            body_html=body_html,
            received_at=received_at,
            is_read=is_read,
            is_starred=item.get("flag", {}).get("flagStatus") == "flagged",
            is_important=is_important,
            labels=labels,
            has_attachments=bool(item.get("hasAttachments", False))
        )

    async def _handle_graph_request(self, method: str, url: str, headers: Dict[str, str], **kwargs) -> httpx.Response:
        """Executa requisição com tratamento seguro de Rate Limiting (HTTP 429) e Retry-After"""
        max_retries = 2
        delay = 1.0

        async with httpx.AsyncClient(timeout=25.0) as client:
            for attempt in range(max_retries + 1):
                resp = await client.request(method, url, headers=headers, **kwargs)
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    sleep_sec = float(retry_after) if retry_after else delay
                    logger.warning(f"Microsoft Graph Rate Limit (429). Aguardando {sleep_sec}s...")
                    await asyncio.sleep(min(sleep_sec, 5.0))
                    delay *= 2
                    continue
                return resp
            return resp

    async def sync_messages(
        self,
        tokens: Dict[str, Any],
        limit: int = 100,
        page_token: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> Tuple[List[NormalizedEmail], Optional[str], Optional[str]]:
        headers = {
            "Authorization": f"Bearer {tokens.get('access_token')}",
            "Prefer": 'outlook.body-content-type="text"'
        }
        
        # Endpoint de mensagens
        url = page_token if page_token else f"{MS_GRAPH_API_BASE}/me/messages"
        params: Dict[str, Any] = {}
        
        if not page_token:
            params["$top"] = min(limit, 100)
            params["$select"] = "id,conversationId,from,toRecipients,subject,bodyPreview,body,receivedDateTime,isRead,importance,flag,categories,hasAttachments"
            params["$orderby"] = "receivedDateTime desc"
            if since:
                since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
                params["$filter"] = f"receivedDateTime ge {since_iso}"

        resp = await self._handle_graph_request("GET", url, headers=headers, params=params if not page_token else None)
        
        if resp.status_code == 401:
            raise PermissionError("Token da conta Microsoft expirado ou inválido (REAUTH_REQUIRED)")
        if resp.status_code != 200:
            logger.error(f"Erro ao listar mensagens Outlook: {resp.text}")
            return [], None, None

        data = resp.json()
        raw_items = data.get("value", [])
        next_link = data.get("@odata.nextLink")
        delta_link = data.get("@odata.deltaLink")

        normalized = [self._normalize_outlook_message(item) for item in raw_items]
        return normalized, next_link, delta_link

    async def get_message(self, tokens: Dict[str, Any], external_id: str) -> Optional[NormalizedEmail]:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        resp = await self._handle_graph_request(
            "GET",
            f"{MS_GRAPH_API_BASE}/me/messages/{external_id}",
            headers=headers
        )
        if resp.status_code == 200:
            return self._normalize_outlook_message(resp.json())
        return None

    async def mark_read(self, tokens: Dict[str, Any], external_id: str, is_read: bool = True) -> bool:
        headers = {
            "Authorization": f"Bearer {tokens.get('access_token')}",
            "Content-Type": "application/json"
        }
        resp = await self._handle_graph_request(
            "PATCH",
            f"{MS_GRAPH_API_BASE}/me/messages/{external_id}",
            headers=headers,
            json={"isRead": is_read}
        )
        return resp.status_code == 200

    async def archive_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        # No Outlook/Graph, mover para pasta 'archive'
        headers = {
            "Authorization": f"Bearer {tokens.get('access_token')}",
            "Content-Type": "application/json"
        }
        resp = await self._handle_graph_request(
            "POST",
            f"{MS_GRAPH_API_BASE}/me/messages/{external_id}/move",
            headers=headers,
            json={"destinationId": "archive"}
        )
        return resp.status_code in [200, 201]

    async def trash_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        resp = await self._handle_graph_request(
            "POST",
            f"{MS_GRAPH_API_BASE}/me/messages/{external_id}/move",
            headers={"Authorization": f"Bearer {tokens.get('access_token')}", "Content-Type": "application/json"},
            json={"destinationId": "deleteditems"}
        )
        return resp.status_code in [200, 201]

    async def send_reply(
        self,
        tokens: Dict[str, Any],
        thread_id: str,
        to_address: str,
        subject: str,
        body_text: str,
        in_reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {tokens.get('access_token')}",
            "Content-Type": "application/json"
        }
        
        # Envia e-mail via Graph sendMail
        payload = {
            "message": {
                "subject": subject if subject.startswith("Re:") else f"Re: {subject}",
                "body": {
                    "contentType": "Text",
                    "content": body_text
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "address": to_address
                        }
                    }
                ]
            },
            "saveToSentItems": "true"
        }

        resp = await self._handle_graph_request(
            "POST",
            f"{MS_GRAPH_API_BASE}/me/sendMail",
            headers=headers,
            json=payload
        )
        if resp.status_code not in [200, 202]:
            logger.error(f"Erro ao enviar resposta via Microsoft Graph: {resp.text}")
            raise ValueError("Falha ao enviar resposta via Outlook")
        return {"status": "sent", "to": to_address}

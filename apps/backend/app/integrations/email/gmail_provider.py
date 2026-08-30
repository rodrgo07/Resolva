import base64
import email
from email.header import decode_header
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import httpx
from urllib.parse import urlencode

from app.integrations.email.base import EmailProvider, NormalizedEmail
from app.integrations.email.sanitizer import sanitize_html_content, html_to_plain_text
from app.core.logging import logger

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://www.googleapis.com/oauth2/v2/userinfo"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"

SCOPES = [
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/gmail.modify"
]

class GmailProvider(EmailProvider):
    def __init__(self, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        self.client_id = client_id or ""
        self.client_secret = client_secret or ""

    async def get_authorization_url(self, state: str, redirect_uri: str, code_challenge: Optional[str] = None) -> str:
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": " ".join(SCOPES),
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        if code_challenge:
            params["code_challenge"] = code_challenge
            params["code_challenge_method"] = "S256"
        return f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri
        }
        if code_verifier:
            data["code_verifier"] = code_verifier

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
            if resp.status_code != 200:
                logger.error(f"Erro no token exchange Gmail: {resp.text}")
                raise ValueError(f"Falha na autenticacao Google: {resp.text}")
            return resp.json()

    async def get_user_profile(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(GOOGLE_USERINFO_ENDPOINT, headers=headers)
            if resp.status_code != 200:
                logger.error(f"Erro ao obter perfil Gmail: {resp.text}")
                raise ValueError("Nao foi possivel obter perfil do Gmail")
            return resp.json()

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(GOOGLE_TOKEN_ENDPOINT, data=data)
            if resp.status_code != 200:
                logger.error(f"Erro ao atualizar token Gmail: {resp.text}")
                raise ValueError("Nao foi possivel atualizar o token de acesso do Gmail")
            return resp.json()

    def _decode_raw_body(self, payload: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
        """Extrai plain text e html de parts do Gmail payload"""
        body_text = None
        body_html = None

        def recurse_parts(part: Dict[str, Any]):
            nonlocal body_text, body_html
            mime_type = part.get("mimeType", "")
            body = part.get("body", {})
            data = body.get("data")
            if data:
                try:
                    # Gmail usa URL-safe base64
                    decoded = base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="replace")
                    if mime_type == "text/plain" and not body_text:
                        body_text = decoded
                    elif mime_type == "text/html" and not body_html:
                        body_html = decoded
                except Exception as e:
                    logger.debug(f"Erro ao decodificar part do email: {e}")

            for subpart in part.get("parts", []):
                recurse_parts(subpart)

        recurse_parts(payload)
        return body_text, body_html

    def _normalize_gmail_message(self, item: Dict[str, Any]) -> NormalizedEmail:
        headers_list = item.get("payload", {}).get("headers", [])
        headers = {h["name"].lower(): h["value"] for h in headers_list}

        subject = headers.get("subject", "(Sem assunto)")
        from_str = headers.get("from", "")
        from_name = None
        from_addr = from_str

        if "<" in from_str and ">" in from_str:
            parts = from_str.split("<")
            from_name = parts[0].strip().strip('"\'')
            from_addr = parts[1].split(">")[0].strip()

        to_str = headers.get("to", "")
        to_addresses = [a.strip() for a in to_str.split(",") if a.strip()]

        internal_date_ms = int(item.get("internalDate", 0))
        if internal_date_ms > 0:
            received_at = datetime.fromtimestamp(internal_date_ms / 1000.0)
        else:
            received_at = datetime.now()

        label_ids = item.get("labelIds", [])
        is_read = "UNREAD" not in label_ids
        is_starred = "STARRED" in label_ids
        is_important = "IMPORTANT" in label_ids

        snippet = item.get("snippet", "")
        body_text, body_html = self._decode_raw_body(item.get("payload", {}))
        
        if not body_text and body_html:
            body_text = html_to_plain_text(body_html)
        if not body_text and snippet:
            body_text = snippet

        sanitized_html = sanitize_html_content(body_html) if body_html else None

        return NormalizedEmail(
            external_id=item["id"],
            thread_id=item.get("threadId"),
            from_address=from_addr,
            from_name=from_name,
            to_addresses=to_addresses,
            subject=subject,
            body_preview=snippet[:250] if snippet else (body_text[:250] if body_text else None),
            body_text=body_text,
            body_html=sanitized_html,
            received_at=received_at,
            is_read=is_read,
            is_starred=is_starred,
            is_important=is_important,
            labels=label_ids
        )

    async def sync_messages(
        self,
        tokens: Dict[str, Any],
        limit: int = 100,
        page_token: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> Tuple[List[NormalizedEmail], Optional[str], Optional[str]]:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        
        params: Dict[str, Any] = {"maxResults": min(limit, 100)}
        if page_token:
            params["pageToken"] = page_token
        
        # Filtro de data recente se fornecido
        query_parts = []
        if since:
            timestamp = int(since.timestamp())
            query_parts.append(f"after:{timestamp}")
        if query_parts:
            params["q"] = " ".join(query_parts)

        async with httpx.AsyncClient(timeout=25.0) as client:
            list_res = await client.get(f"{GMAIL_API_BASE}/messages", headers=headers, params=params)
            if list_res.status_code == 401:
                raise PermissionError("Token do Gmail expirado ou invalido")
            if list_res.status_code != 200:
                logger.error(f"Erro ao listar mensagens Gmail: {list_res.text}")
                return [], None, None

            data = list_res.json()
            messages_meta = data.get("messages", [])
            next_token = data.get("nextPageToken")
            history_id = str(data.get("resultSizeEstimate", ""))

            normalized_list: List[NormalizedEmail] = []
            for m in messages_meta:
                msg_id = m["id"]
                msg_res = await client.get(f"{GMAIL_API_BASE}/messages/{msg_id}", headers=headers, params={"format": "full"})
                if msg_res.status_code == 200:
                    normalized = self._normalize_gmail_message(msg_res.json())
                    normalized_list.append(normalized)

            return normalized_list, next_token, history_id

    async def get_message(self, tokens: Dict[str, Any], external_id: str) -> Optional[NormalizedEmail]:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(f"{GMAIL_API_BASE}/messages/{external_id}", headers=headers, params={"format": "full"})
            if resp.status_code == 200:
                return self._normalize_gmail_message(resp.json())
            return None

    async def mark_read(self, tokens: Dict[str, Any], external_id: str, is_read: bool = True) -> bool:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        body = {
            "removeLabelIds": ["UNREAD"] if is_read else [],
            "addLabelIds": [] if is_read else ["UNREAD"]
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{GMAIL_API_BASE}/messages/{external_id}/modify", headers=headers, json=body)
            return resp.status_code == 200

    async def archive_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        body = {"removeLabelIds": ["INBOX"]}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{GMAIL_API_BASE}/messages/{external_id}/modify", headers=headers, json=body)
            return resp.status_code == 200

    async def trash_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        headers = {"Authorization": f"Bearer {tokens.get('access_token')}"}
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{GMAIL_API_BASE}/messages/{external_id}/trash", headers=headers)
            return resp.status_code == 200

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
        
        # Constrói mensagem MIME RFC 2822
        from email.mime.text import MIMEText
        mime_msg = MIMEText(body_text)
        mime_msg["to"] = to_address
        mime_msg["subject"] = subject if subject.startswith("Re:") else f"Re: {subject}"
        if in_reply_to:
            mime_msg["In-Reply-To"] = in_reply_to
            mime_msg["References"] = in_reply_to

        raw = base64.urlsafe_b64encode(mime_msg.as_bytes()).decode("ASCII")
        post_data = {
            "raw": raw,
            "threadId": thread_id
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(f"{GMAIL_API_BASE}/messages/send", headers=headers, json=post_data)
            if resp.status_code != 200:
                logger.error(f"Erro ao enviar resposta Gmail: {resp.text}")
                raise ValueError("Falha ao enviar resposta via Gmail")
            return resp.json()

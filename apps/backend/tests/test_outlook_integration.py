import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from datetime import datetime
from app.integrations.email.outlook_provider import OutlookProvider
from app.integrations.email.mock_provider import MockEmailProvider
from app.integrations.email.sanitizer import sanitize_html_content

@pytest.mark.asyncio
async def test_outlook_provider_normalization():
    provider = OutlookProvider(client_id="test_client_id")
    raw_graph_item = {
        "id": "AAMkADk1234567890=",
        "conversationId": "AAQkADk112233=",
        "from": {
            "emailAddress": {
                "name": "Equipe Microsoft 365",
                "address": "noreply@microsoft.com"
            }
        },
        "toRecipients": [
            {
                "emailAddress": {
                    "name": "Rodrigo",
                    "address": "usuario@outlook.com"
                }
            }
        ],
        "subject": "Segurança da Conta Microsoft: Novo login detectado",
        "bodyPreview": "Detectamos um login a partir de um novo navegador.",
        "body": {
            "contentType": "html",
            "content": "<div><p>Detectamos um login no <strong>Windows 11</strong>.</p><script>alert('xss');</script></div>"
        },
        "receivedDateTime": "2026-08-29T18:30:00Z",
        "isRead": False,
        "importance": "high",
        "flag": {"flagStatus": "flagged"},
        "categories": ["Security"],
        "hasAttachments": False
    }

    normalized = provider._normalize_outlook_message(raw_graph_item)
    assert normalized.external_id == "AAMkADk1234567890="
    assert normalized.thread_id == "AAQkADk112233="
    assert normalized.from_address == "noreply@microsoft.com"
    assert normalized.from_name == "Equipe Microsoft 365"
    assert normalized.to_addresses == ["usuario@outlook.com"]
    assert normalized.subject == "Segurança da Conta Microsoft: Novo login detectado"
    assert normalized.is_read == False
    assert normalized.is_important == True
    assert normalized.is_starred == True
    # Verifica sanitização HTML
    assert "<script>" not in normalized.body_html
    assert "Windows 11" in normalized.body_text

@pytest.mark.asyncio
async def test_outlook_oauth_url_generation():
    provider = OutlookProvider(client_id="ms_client_abc", tenant_id="common")
    url = await provider.get_authorization_url(state="state_outlook_123", redirect_uri="http://localhost:8700/api/emails/connect/callback")
    assert "login.microsoftonline.com/common/oauth2/v2.0/authorize" in url
    assert "client_id=ms_client_abc" in url
    assert "state=state_outlook_123" in url
    assert "Mail.Read" in url

@pytest.mark.asyncio
async def test_outlook_api_and_multi_provider_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Init OAuth Outlook
        init_res = await ac.post("/api/emails/connect/outlook/init")
        assert init_res.status_code == 200
        data = init_res.json()
        assert "authorization_url" in data
        assert data["provider"] == "outlook"

        # 2. Conectar conta Mock Outlook
        connect_res = await ac.post("/api/emails/connect/mock?provider=outlook")
        assert connect_res.status_code == 200
        acc_data = connect_res.json()
        assert acc_data["provider"] == "outlook"
        assert acc_data["email_address"] == "usuario@outlook.com"

        # 3. Listar contas unificadas (Gmail + Outlook)
        accounts_res = await ac.get("/api/emails/accounts")
        assert accounts_res.status_code == 200
        accs = accounts_res.json()
        assert len(accs) >= 1

        # 4. Sincronizar e-mails da conta Outlook
        sync_res = await ac.post(f"/api/emails/sync?provider=outlook")
        assert sync_res.status_code == 200
        assert sync_res.json()["status"] == "success"

        # 5. Listar e-mails com filtro de provider
        outlook_emails_res = await ac.get("/api/emails/?provider=outlook")
        assert outlook_emails_res.status_code == 200
        outlook_emails = outlook_emails_res.json()
        assert outlook_emails["total"] > 0
        assert any(e["provider"] == "outlook" for e in outlook_emails["items"])

        # 6. Resumo estatístico com filtro por provedor
        summary_outlook = await ac.get("/api/emails/summary?provider=outlook")
        assert summary_outlook.status_code == 200
        assert "unread_count" in summary_outlook.json()

        # 7. Resumo global de todos os provedores
        summary_all = await ac.get("/api/emails/summary")
        assert summary_all.status_code == 200
        assert summary_all.json()["total_count"] >= outlook_emails["total"]

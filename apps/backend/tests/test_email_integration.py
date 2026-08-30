import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app
from datetime import datetime
from unittest.mock import AsyncMock, patch
from app.integrations.email.sanitizer import sanitize_html_content, html_to_plain_text
from app.integrations.email.classifier import classify_email
from app.core.security import token_storage
from app.integrations.email.mock_provider import MockEmailProvider
from app.integrations.email.gmail_provider import GmailProvider

@pytest.mark.asyncio
async def test_email_sanitization():
    unsafe_html = """
    <div>
        <p>Olá amigo!</p>
        <script>alert('xss');</script>
        <iframe src="http://evil.com"></iframe>
        <a href="javascript:doEvil()" onclick="stealTokens()">Clique aqui</a>
        <img src="http://example.com/logo.png" onload="alert('hack')"/>
    </div>
    """
    cleaned = sanitize_html_content(unsafe_html)
    assert "<script>" not in cleaned
    assert "<iframe>" not in cleaned
    assert "onclick=" not in cleaned
    assert "onload=" not in cleaned
    assert "javascript:" not in cleaned
    assert "Olá amigo!" in cleaned

    plain = html_to_plain_text(unsafe_html)
    assert "Olá amigo!" in plain
    assert "alert" not in plain

@pytest.mark.asyncio
async def test_email_ai_classification():
    # Crítico
    cls, reasoning, reply = classify_email(
        subject="[URGENTE] Bloqueio imediato da conta bancária",
        from_address="alerta@banco.com.br",
        body_text="Favor responder imediatamente para evitar fraude."
    )
    assert cls == "CRITICAL"
    assert reply == True

    # Importante
    cls2, reasoning2, reply2 = classify_email(
        subject="Fatura do cartão de crédito",
        from_address="financeiro@empresa.com",
        body_text="Segue boleto para pagamento do projeto Resolva."
    )
    assert cls2 == "IMPORTANT"

    # Newsletter
    cls3, reasoning3, reply3 = classify_email(
        subject="Resumo semanal de notícias tech",
        from_address="noreply@techdaily.com",
        body_text="Clique aqui para descadastre-se da newsletter."
    )
    assert cls3 == "NEWSLETTER"
    assert reply3 == False

@pytest.mark.asyncio
async def test_token_storage_vault():
    account_id = 9999
    tokens = {
        "access_token": "secret_access_token_12345",
        "refresh_token": "secret_refresh_token_67890",
        "token_type": "Bearer"
    }
    await token_storage.save_tokens(account_id, tokens)
    
    # Recupera
    retrieved = await token_storage.get_tokens(account_id)
    assert retrieved is not None
    assert retrieved["access_token"] == "secret_access_token_12345"
    assert retrieved["refresh_token"] == "secret_refresh_token_67890"

    # Deleta
    deleted = await token_storage.delete_tokens(account_id)
    assert deleted == True
    assert (await token_storage.get_tokens(account_id)) is None

@pytest.mark.asyncio
async def test_mock_email_provider_flow():
    provider = MockEmailProvider()
    auth_url = await provider.get_authorization_url(state="xyz", redirect_uri="http://test")
    assert "state=xyz" in auth_url

    tokens = await provider.exchange_code_for_tokens(code="mock_code", redirect_uri="http://test")
    assert "access_token" in tokens

    profile = await provider.get_user_profile(tokens)
    assert profile["email"] == "usuario@resolva.local"

    msgs, next_token, history_id = await provider.sync_messages(tokens, limit=10)
    assert len(msgs) > 0
    assert msgs[0].subject != ""

@pytest.mark.asyncio
async def test_email_api_full_flow():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # 1. Init OAuth Gmail
        init_res = await ac.post("/api/emails/connect/gmail/init")
        assert init_res.status_code == 200
        assert "authorization_url" in init_res.json()
        assert "state" in init_res.json()

        # 2. Conectar Mock Account
        mock_acc_res = await ac.post("/api/emails/connect/mock")
        assert mock_acc_res.status_code == 200
        acc_data = mock_acc_res.json()
        acc_id = acc_data["id"]
        assert acc_data["email_address"] == "usuario@resolva.local"

        # 3. Listar Contas
        accounts_res = await ac.get("/api/emails/accounts")
        assert accounts_res.status_code == 200
        assert len(accounts_res.json()) >= 1

        # 4. Sincronizar
        sync_res = await ac.post(f"/api/emails/sync?account_id={acc_id}")
        assert sync_res.status_code == 200
        assert sync_res.json()["status"] == "success"

        # 5. Listar Emails
        emails_res = await ac.get("/api/emails/?page=1&page_size=10")
        assert emails_res.status_code == 200
        emails_data = emails_res.json()
        assert emails_data["total"] > 0
        email_item = emails_data["items"][0]
        email_id = email_item["id"]

        # 6. Resumo / Estatísticas
        summary_res = await ac.get("/api/emails/summary")
        assert summary_res.status_code == 200
        summary_data = summary_res.json()
        assert summary_data["total_count"] > 0

        # 7. Marcar como lido
        read_res = await ac.post(f"/api/emails/{email_id}/read?is_read=true")
        assert read_res.status_code == 200
        assert read_res.json()["is_read"] == True

        # 8. Arquivar email
        archive_res = await ac.post(f"/api/emails/{email_id}/archive")
        assert archive_res.status_code == 200
        assert archive_res.json()["success"] == True

        # 9. Responder com confirmação necessária
        reply_unconfirmed = await ac.post(f"/api/emails/{email_id}/reply", json={"body": "Ok", "confirmed": False})
        assert reply_unconfirmed.status_code == 400

        reply_confirmed = await ac.post(f"/api/emails/{email_id}/reply", json={"body": "Confirmado!", "confirmed": True})
        assert reply_confirmed.status_code == 200

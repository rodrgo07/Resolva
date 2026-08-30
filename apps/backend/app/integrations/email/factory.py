from typing import Dict, Any, Optional
from app.integrations.email.base import EmailProvider
from app.integrations.email.gmail_provider import GmailProvider
from app.integrations.email.mock_provider import MockEmailProvider
from app.integrations.email.outlook_provider import OutlookProvider
from app.config import settings

def get_email_provider(provider_name: str = "gmail") -> EmailProvider:
    provider_name = provider_name.lower().strip()
    if provider_name == "gmail":
        if not settings.GMAIL_CLIENT_ID:
            return MockEmailProvider()
        return GmailProvider(client_id=settings.GMAIL_CLIENT_ID, client_secret=settings.GMAIL_CLIENT_SECRET)
    elif provider_name in ["outlook", "microsoft"]:
        if not settings.OUTLOOK_CLIENT_ID:
            return MockEmailProvider()
        return OutlookProvider(
            client_id=settings.OUTLOOK_CLIENT_ID,
            client_secret=settings.OUTLOOK_CLIENT_SECRET,
            tenant_id=settings.OUTLOOK_TENANT_ID
        )
    elif provider_name == "mock":
        return MockEmailProvider()
    else:
        raise ValueError(f"Provedor de e-mail não suportado: {provider_name}")

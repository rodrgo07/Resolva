from typing import Dict, Any, Optional
from app.integrations.email.base import EmailProvider
from app.integrations.email.gmail_provider import GmailProvider
from app.integrations.email.mock_provider import MockEmailProvider
from app.integrations.email.outlook_provider import OutlookProvider
from app.config import settings

def get_email_provider(provider_name: str = "gmail") -> EmailProvider:
    provider_name = provider_name.lower().strip()
    if provider_name == "gmail":
        # Se client_id nao estiver configurado, podemos usar Mock se solicitado ou instanciar GmailProvider
        return GmailProvider(client_id=settings.GMAIL_CLIENT_ID, client_secret=settings.GMAIL_CLIENT_SECRET)
    elif provider_name == "mock":
        return MockEmailProvider()
    elif provider_name == "outlook":
        return OutlookProvider()
    else:
        raise ValueError(f"Provedor de email nao suportado: {provider_name}")

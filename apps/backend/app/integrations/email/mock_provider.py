from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from app.integrations.email.base import EmailProvider, NormalizedEmail

class MockEmailProvider(EmailProvider):
    """
    Provedor Mock com suporte a cenarios multi-provedor (Gmail, Outlook),
    paginacao, rate limit (429), token expirado e e-mails duplicados.
    """
    def __init__(self):
        self.mock_emails = [
            NormalizedEmail(
                external_id="mock_gmail_001",
                thread_id="mock_thread_g1",
                from_address="diretoria@empresa.com",
                from_name="Diretoria Resolva",
                to_addresses=["usuario@resolva.local"],
                subject="[URGENTE] Relatório Semestral e Alinhamento",
                body_preview="Rodrigo, precisamos fechar os números do trimestre com urgência para a diretoria.",
                body_text="Olá Rodrigo,\n\nPrecisamos fechar os números do trimestre com urgência para a diretoria até amanhã às 14:00.\nPor favor responda este e-mail confirmando o envio dos dados.\n\nAtenciosamente,\nDiretoria Executiva",
                body_html="<p>Olá Rodrigo,</p><p>Precisamos fechar os números do trimestre com <strong>urgência</strong> para a diretoria até amanhã às 14:00.</p>",
                received_at=datetime.now() - timedelta(minutes=25),
                is_read=False,
                is_starred=True,
                is_important=True,
                labels=["INBOX", "IMPORTANT", "UNREAD"]
            ),
            NormalizedEmail(
                external_id="mock_outlook_002",
                thread_id="mock_thread_o2",
                from_address="contato@microsoft.com",
                from_name="Microsoft 365 Security",
                to_addresses=["usuario@resolva.local"],
                subject="Alerta de Segurança: Novo Login Detectado no Outlook",
                body_preview="Detectamos um acesso à sua conta Microsoft a partir de um novo dispositivo Windows.",
                body_text="Olá Rodrigo,\n\nDetectamos um novo login em sua conta Microsoft 365.\nSe foi você, nenhuma ação é necessária. Caso contrário, acesse as configurações de segurança para revisar suas credenciais.",
                body_html="<p>Olá Rodrigo,</p><p>Detectamos um <strong>novo login</strong> em sua conta Microsoft 365.</p>",
                received_at=datetime.now() - timedelta(hours=1),
                is_read=False,
                is_starred=False,
                is_important=True,
                labels=["INBOX", "UNREAD"]
            ),
            NormalizedEmail(
                external_id="mock_gmail_003",
                thread_id="mock_thread_g3",
                from_address="financeiro@banco.com.br",
                from_name="Banco Digital",
                to_addresses=["usuario@resolva.local"],
                subject="Fatura do Cartão Disponível para Pagamento",
                body_preview="Sua fatura fechou. O valor total é de R$ 850,00 com vencimento em 5 dias.",
                body_text="Olá Rodrigo,\n\nSua fatura de cartão de crédito fechou com o valor de R$ 850,00.\nVencimento: 05/09/2026.\nEvite juros pagando em dia pelo aplicativo do banco.",
                body_html="<p>Olá Rodrigo,</p><p>Sua fatura fechou no valor de <strong>R$ 850,00</strong>.</p>",
                received_at=datetime.now() - timedelta(hours=3),
                is_read=False,
                is_starred=False,
                is_important=True,
                labels=["INBOX", "UNREAD"]
            ),
            NormalizedEmail(
                external_id="mock_outlook_004",
                thread_id="mock_thread_o4",
                from_address="suporte@faculdade.edu.br",
                from_name="Secretaria Acadêmica",
                to_addresses=["usuario@resolva.local"],
                subject="Aviso sobre Matrícula e Calendário de Estudos",
                body_preview="O período de confirmação de disciplinas do semestre já está aberto no portal.",
                body_text="Prezado aluno Rodrigo,\n\nInformamos que o período de confirmação de disciplinas do semestre está aberto até o dia 10.\nNão deixe para a última hora.",
                body_html="<p>Prezado aluno Rodrigo,</p><p>O período de confirmação de matrícula está aberto.</p>",
                received_at=datetime.now() - timedelta(hours=8),
                is_read=True,
                is_starred=False,
                is_important=False,
                labels=["INBOX"]
            ),
            NormalizedEmail(
                external_id="mock_msg_005",
                thread_id="mock_thread_005",
                from_address="news@techdaily.io",
                from_name="Tech Daily Newsletter",
                to_addresses=["usuario@resolva.local"],
                subject="Novidades em Inteligência Artificial e Rust Tauri",
                body_preview="Confira os destaques da semana no mundo da tecnologia e desenvolvimento desktop.",
                body_text="Nesta edição: Melhores práticas com Tauri v2, agentes autônomos com function calling e muito mais.",
                body_html="<h3>Tech Daily</h3><p>Nesta edição: Melhores práticas com Tauri v2.</p>",
                received_at=datetime.now() - timedelta(days=1),
                is_read=True,
                is_starred=False,
                is_important=False,
                labels=["NEWSLETTER"]
            )
        ]

    async def get_authorization_url(self, state: str, redirect_uri: str) -> str:
        return f"http://localhost:8700/api/emails/connect/callback?code=mock_auth_code_123&state={state}"

    async def exchange_code_for_tokens(self, code: str, redirect_uri: str, code_verifier: Optional[str] = None) -> Dict[str, Any]:
        return {
            "access_token": "mock_access_token_xyz",
            "refresh_token": "mock_refresh_token_abc",
            "expires_in": 3600,
            "token_type": "Bearer"
        }

    async def get_user_profile(self, tokens: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": "mock_ms_id_789",
            "email": "usuario@outlook.com",
            "name": "Rodrigo (Outlook)"
        }

    async def refresh_tokens(self, refresh_token: str) -> Dict[str, Any]:
        if refresh_token == "invalid_refresh_token":
            raise PermissionError("Refresh token inválido ou expirado (REAUTH_REQUIRED)")
        return {
            "access_token": "mock_refreshed_access_token_456",
            "expires_in": 3600
        }

    async def sync_messages(
        self,
        tokens: Dict[str, Any],
        limit: int = 100,
        page_token: Optional[str] = None,
        since: Optional[datetime] = None
    ) -> Tuple[List[NormalizedEmail], Optional[str], Optional[str]]:
        if tokens.get("access_token") == "simulate_rate_limit":
            # Simula recuperação de rate limit
            return self.mock_emails[:limit], None, "mock_history_delta"
        return self.mock_emails[:limit], None, "mock_history_100"

    async def get_message(self, tokens: Dict[str, Any], external_id: str) -> Optional[NormalizedEmail]:
        for em in self.mock_emails:
            if em.external_id == external_id:
                return em
        return None

    async def mark_read(self, tokens: Dict[str, Any], external_id: str, is_read: bool = True) -> bool:
        for em in self.mock_emails:
            if em.external_id == external_id:
                em.is_read = is_read
                return True
        return True

    async def archive_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        for em in self.mock_emails:
            if em.external_id == external_id:
                if "INBOX" in em.labels:
                    em.labels.remove("INBOX")
                return True
        return True

    async def trash_message(self, tokens: Dict[str, Any], external_id: str) -> bool:
        for em in self.mock_emails:
            if em.external_id == external_id:
                em.labels = ["TRASH"]
                return True
        return True

    async def send_reply(
        self,
        tokens: Dict[str, Any],
        thread_id: str,
        to_address: str,
        subject: str,
        body_text: str,
        in_reply_to: Optional[str] = None
    ) -> Dict[str, Any]:
        return {"id": "mock_sent_msg_777", "threadId": thread_id, "status": "sent"}

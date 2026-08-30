from typing import Dict, Any, List, Optional
from app.ai.tools.base import BaseTool
from app.repositories.email_repository import EmailRepository

class ListImportantEmailsTool(BaseTool):
    name = "list_important_emails"
    description = "Consulta no Resolva e lista os e-mails classificados como urgentes ou importantes pela triagem de IA. Suporta filtro por provedor (gmail, outlook ou all)."
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "enum": ["all", "gmail", "outlook"], "description": "Filtro opcional por provedor de e-mail (gmail ou outlook)", "default": "all"},
            "limit": {"type": "integer", "description": "Número máximo de e-mails para listar", "default": 10}
        }
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        repo = EmailRepository(db)
        limit = args.get("limit", 10)
        provider = args.get("provider", "all")
        emails, total = await repo.list_emails(provider=provider, filter_type="important", limit=limit)
        return {
            "total_important": total,
            "provider": provider,
            "emails": [
                {
                    "id": e.id,
                    "provider": e.account.provider if hasattr(e, "account") and e.account else "local",
                    "from": e.from_name or e.from_address,
                    "subject": e.subject,
                    "snippet": e.body_preview,
                    "received_at": str(e.received_at),
                    "classification": e.ai_classification,
                    "needs_reply": e.needs_reply
                }
                for e in emails
            ]
        }

class SearchEmailsTool(BaseTool):
    name = "search_emails"
    description = "Pesquisa e-mails na caixa local unificada do Resolva (Gmail + Outlook) por termo ou palavra-chave (ex: faculdade, boleto, pagamento, projeto, reunião)."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Termo de busca"},
            "provider": {"type": "string", "enum": ["all", "gmail", "outlook"], "description": "Provedor a consultar", "default": "all"},
            "limit": {"type": "integer", "description": "Limite de resultados", "default": 10}
        },
        "required": ["query"]
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        repo = EmailRepository(db)
        q = args.get("query", "")
        provider = args.get("provider", "all")
        limit = args.get("limit", 10)
        emails, total = await repo.list_emails(provider=provider, search_query=q, limit=limit)
        return {
            "query": q,
            "provider": provider,
            "total_found": total,
            "emails": [
                {
                    "id": e.id,
                    "provider": e.account.provider if hasattr(e, "account") and e.account else "local",
                    "from": e.from_name or e.from_address,
                    "subject": e.subject,
                    "preview": e.body_preview,
                    "received_at": str(e.received_at),
                    "is_read": e.is_read
                }
                for e in emails
            ]
        }

class GetUnreadEmailsTool(BaseTool):
    name = "get_unread_emails"
    description = "Retorna a lista de e-mails não lidos unificados de todas as contas conectadas (Gmail e Outlook)."
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "enum": ["all", "gmail", "outlook"], "description": "Filtrar por provedor", "default": "all"},
            "limit": {"type": "integer", "description": "Limite de e-mails", "default": 10}
        }
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        repo = EmailRepository(db)
        provider = args.get("provider", "all")
        emails, total = await repo.list_emails(provider=provider, filter_type="unread", limit=args.get("limit", 10))
        return {
            "unread_count": total,
            "provider": provider,
            "emails": [
                {
                    "id": e.id,
                    "provider": e.account.provider if hasattr(e, "account") and e.account else "local",
                    "from": e.from_name or e.from_address,
                    "subject": e.subject,
                    "received_at": str(e.received_at),
                    "classification": e.ai_classification
                }
                for e in emails
            ]
        }

class GetEmailSummaryTool(BaseTool):
    name = "get_email_summary"
    description = "Retorna o panorama geral da caixa postal (Gmail + Outlook): contagem de não lidos, urgentes, importantes e mensagens aguardando resposta."
    parameters = {
        "type": "object",
        "properties": {
            "provider": {"type": "string", "enum": ["all", "gmail", "outlook"], "description": "Filtrar resumo por provedor", "default": "all"}
        }
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        repo = EmailRepository(db)
        provider = args.get("provider", "all")
        stats = await repo.get_summary_stats(provider=provider)
        return {"provider": provider, **stats}

class ArchiveEmailTool(BaseTool):
    name = "archive_email"
    description = "Arquiva um e-mail específico pelo seu ID local. Requer confirmação explícita do usuário."
    parameters = {
        "type": "object",
        "properties": {
            "email_id": {"type": "integer", "description": "ID local do email a arquivar"}
        },
        "required": ["email_id"]
    }
    permission_level = "WRITE"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        from app.services.email_service import EmailService
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        service = EmailService(db)
        email_id = args["email_id"]
        try:
            await service.archive_email(email_id)
            return {"success": True, "message": f"Email {email_id} arquivado com sucesso."}
        except Exception as e:
            return {"error": str(e)}

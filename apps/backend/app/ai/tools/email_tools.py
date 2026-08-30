from typing import Dict, Any, List, Optional
from app.ai.tools.base import BaseTool
from app.repositories.email_repository import EmailRepository

class ListImportantEmailsTool(BaseTool):
    name = "list_important_emails"
    description = "Consulta no Resolva e lista os e-mails classificados como urgentes ou importantes pela triagem de IA."
    parameters = {
        "type": "object",
        "properties": {
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
        emails, total = await repo.list_emails(filter_type="important", limit=limit)
        return {
            "total_important": total,
            "emails": [
                {
                    "id": e.id,
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
    description = "Pesquisa e-mails na caixa local do Resolva por termo ou palavra-chave (ex: faculdade, boleto, pagamento, projeto)."
    parameters = {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Termo de busca"},
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
        limit = args.get("limit", 10)
        emails, total = await repo.list_emails(search_query=q, limit=limit)
        return {
            "query": q,
            "total_found": total,
            "emails": [
                {
                    "id": e.id,
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
    description = "Retorna a lista de e-mails não lidos armazenados localmente."
    parameters = {
        "type": "object",
        "properties": {
            "limit": {"type": "integer", "description": "Limite de e-mails", "default": 10}
        }
    }
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        repo = EmailRepository(db)
        emails, total = await repo.list_emails(filter_type="unread", limit=args.get("limit", 10))
        return {
            "unread_count": total,
            "emails": [
                {
                    "id": e.id,
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
    description = "Retorna o panorama geral da caixa postal: contagem de não lidos, urgentes, importantes e mensagens aguardando resposta."
    parameters = {"type": "object", "properties": {}}
    permission_level = "READ"

    async def execute(self, args: Dict[str, Any], services: Dict[str, Any]) -> Dict[str, Any]:
        db = services.get("db")
        if not db:
            return {"error": "Sessão de banco de dados não disponível"}
        repo = EmailRepository(db)
        stats = await repo.get_summary_stats()
        return stats

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

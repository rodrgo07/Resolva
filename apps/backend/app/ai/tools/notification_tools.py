from typing import Dict, Any, List, Optional
from app.ai.tools.base import BaseTool
from app.ai.permissions import PermissionLevel, RiskLevel
from app.notifications.repository import NotificationRepository
from app.notifications.engine import NotificationEngine
from app.schemas.notification import NotificationCreate

class GetNotificationsTool(BaseTool):
    name = "get_notifications"
    description = "Lista as notificações recentes do sistema com suporte a paginação e filtros."
    parameters = {
        "type": "object",
        "properties": {
            "unread_only": {"type": "boolean", "description": "Filtrar apenas não lidas"},
            "source": {"type": "string", "description": "Filtrar por categoria (TASKS, CALENDAR, EMAILS, STUDIES, FINANCES, AGENT)"},
            "limit": {"type": "integer", "description": "Limite máximo de notificações"}
        }
    }
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "notifications"

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> List[Dict[str, Any]]:
        db = context.get("db")
        if not db:
            return []
        repo = NotificationRepository(db)
        unread_only = params.get("unread_only", False)
        source = params.get("source")
        limit = params.get("limit", 10)
        notifs = await repo.list_notifications(limit=limit, unread_only=unread_only, source=source)
        return [
            {
                "id": n.id,
                "type": n.type,
                "title": n.title,
                "message": n.message,
                "priority": n.priority,
                "source": n.source,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat() if n.created_at else None
            }
            for n in notifs
        ]

class GetNotificationSummaryTool(BaseTool):
    name = "get_notification_summary"
    description = "Retorna um resumo de notificações não lidas, urgentes e distribuição por categoria."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "notifications"

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        if not db:
            return {}
        repo = NotificationRepository(db)
        return await repo.get_summary()

class MarkNotificationReadTool(BaseTool):
    name = "mark_notification_read"
    description = "Marca uma notificação específica como lida no sistema."
    parameters = {
        "type": "object",
        "properties": {
            "notification_id": {"type": "integer", "description": "ID da notificação"}
        },
        "required": ["notification_id"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.LOW
    category = "notifications"

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        if not db:
            return {"success": False, "error": "Sem sessão ativa"}
        notif_id = params.get("notification_id")
        if not notif_id:
            return {"success": False, "error": "notification_id é obrigatório"}
        repo = NotificationRepository(db)
        notif = await repo.mark_as_read(int(notif_id))
        return {"success": notif is not None, "notification_id": notif_id}

class DismissNotificationTool(BaseTool):
    name = "dismiss_notification"
    description = "Dispensa / descarta uma notificação."
    parameters = {
        "type": "object",
        "properties": {
            "notification_id": {"type": "integer", "description": "ID da notificação"}
        },
        "required": ["notification_id"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.LOW
    category = "notifications"

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        if not db:
            return {"success": False, "error": "Sem sessão ativa"}
        notif_id = params.get("notification_id")
        if not notif_id:
            return {"success": False, "error": "notification_id é obrigatório"}
        repo = NotificationRepository(db)
        notif = await repo.dismiss(int(notif_id))
        return {"success": notif is not None, "notification_id": notif_id}

class CreateNotificationTool(BaseTool):
    name = "create_notification"
    description = "Cria um aviso ou lembrete inteligente no centro de notificações do usuário."
    parameters = {
        "type": "object",
        "properties": {
            "type": {"type": "string", "description": "Tipo da notificação"},
            "title": {"type": "string", "description": "Título da notificação"},
            "message": {"type": "string", "description": "Mensagem descritiva"},
            "priority": {"type": "string", "description": "LOW, NORMAL, IMPORTANT, URGENT, CRITICAL"}
        },
        "required": ["title", "message"]
    }
    permission_level = PermissionLevel.WRITE
    risk_level = RiskLevel.LOW
    category = "notifications"

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        if not db:
            return {"success": False, "error": "Sem sessão ativa"}
        engine = NotificationEngine(db)
        notif_in = NotificationCreate(
            type=params.get("type", "AGENT_RECOMMENDATION"),
            title=params.get("title", "Aviso do Resolva"),
            message=params.get("message", ""),
            priority=params.get("priority", "NORMAL"),
            source="AGENT",
            source_id=params.get("source_id"),
            action_type=params.get("action_type"),
            action_payload=params.get("action_payload")
        )
        notif = await engine.create_notification(notif_in)
        return {
            "success": notif is not None,
            "id": notif.id if notif else None,
            "title": notif.title if notif else None
        }

class GetNotificationPreferencesTool(BaseTool):
    name = "get_notification_preferences"
    description = "Consulta as preferências atuais de notificação e quiet hours do usuário."
    parameters = {"type": "object", "properties": {}}
    permission_level = PermissionLevel.READ
    risk_level = RiskLevel.LOW
    category = "notifications"

    async def execute(self, params: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        db = context.get("db")
        if not db:
            return {}
        engine = NotificationEngine(db)
        prefs = await engine.get_preferences()
        return prefs.model_dump()

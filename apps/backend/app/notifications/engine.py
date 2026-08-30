import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.notification import Notification
from app.models.settings import AppSetting
from app.models.activity import ActivityLog
from app.schemas.notification import NotificationCreate, NotificationPreferences, NotificationPreferencesUpdate
from app.notifications.repository import NotificationRepository
from app.notifications.policy import NotificationPolicy
from app.notifications.dispatcher import dispatcher
from app.core.logging import logger

class NotificationEngine:
    """
    Motor central de notificações inteligentes, deduplicação, anti-spam,
    verificação de quiet hours e disparo multicanal.
    """
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = NotificationRepository(db)

    async def get_preferences(self) -> NotificationPreferences:
        keys = [
            "notification.enabled",
            "notification.windows_toast_enabled",
            "notification.in_app_enabled",
            "notification.quiet_hours_enabled",
            "notification.quiet_hours_start",
            "notification.quiet_hours_end",
            "notification.allow_critical_in_quiet_hours",
            "notification.min_priority",
            "notification.grouping_enabled",
            "notification.tasks_enabled",
            "notification.calendar_enabled",
            "notification.emails_enabled",
            "notification.studies_enabled",
            "notification.finances_enabled",
            "notification.automations_enabled",
            "notification.agent_enabled",
            "notification.sound_enabled",
        ]
        stmt = select(AppSetting).where(AppSetting.key.in_(keys))
        res = await self.db.execute(stmt)
        settings_map = {s.key: s.value for s in res.scalars().all()}

        return NotificationPreferences(
            enabled=settings_map.get("notification.enabled", "true") == "true",
            windows_toast_enabled=settings_map.get("notification.windows_toast_enabled", "true") == "true",
            in_app_enabled=settings_map.get("notification.in_app_enabled", "true") == "true",
            quiet_hours_enabled=settings_map.get("notification.quiet_hours_enabled", "false") == "true",
            quiet_hours_start=settings_map.get("notification.quiet_hours_start", "22:00"),
            quiet_hours_end=settings_map.get("notification.quiet_hours_end", "07:00"),
            allow_critical_in_quiet_hours=settings_map.get("notification.allow_critical_in_quiet_hours", "true") == "true",
            min_priority=settings_map.get("notification.min_priority", "LOW"),
            grouping_enabled=settings_map.get("notification.grouping_enabled", "true") == "true",
            tasks_enabled=settings_map.get("notification.tasks_enabled", "true") == "true",
            calendar_enabled=settings_map.get("notification.calendar_enabled", "true") == "true",
            emails_enabled=settings_map.get("notification.emails_enabled", "true") == "true",
            studies_enabled=settings_map.get("notification.studies_enabled", "true") == "true",
            finances_enabled=settings_map.get("notification.finances_enabled", "true") == "true",
            automations_enabled=settings_map.get("notification.automations_enabled", "true") == "true",
            agent_enabled=settings_map.get("notification.agent_enabled", "true") == "true",
            sound_enabled=settings_map.get("notification.sound_enabled", "true") == "true",
        )

    async def update_preferences(self, update_data: NotificationPreferencesUpdate) -> NotificationPreferences:
        mapping = {
            "enabled": ("notification.enabled", "boolean"),
            "windows_toast_enabled": ("notification.windows_toast_enabled", "boolean"),
            "in_app_enabled": ("notification.in_app_enabled", "boolean"),
            "quiet_hours_enabled": ("notification.quiet_hours_enabled", "boolean"),
            "quiet_hours_start": ("notification.quiet_hours_start", "string"),
            "quiet_hours_end": ("notification.quiet_hours_end", "string"),
            "allow_critical_in_quiet_hours": ("notification.allow_critical_in_quiet_hours", "boolean"),
            "min_priority": ("notification.min_priority", "string"),
            "grouping_enabled": ("notification.grouping_enabled", "boolean"),
            "tasks_enabled": ("notification.tasks_enabled", "boolean"),
            "calendar_enabled": ("notification.calendar_enabled", "boolean"),
            "emails_enabled": ("notification.emails_enabled", "boolean"),
            "studies_enabled": ("notification.studies_enabled", "boolean"),
            "finances_enabled": ("notification.finances_enabled", "boolean"),
            "automations_enabled": ("notification.automations_enabled", "boolean"),
            "agent_enabled": ("notification.agent_enabled", "boolean"),
            "sound_enabled": ("notification.sound_enabled", "boolean"),
        }

        for field_name, val in update_data.model_dump(exclude_unset=True).items():
            if field_name in mapping:
                setting_key, setting_type = mapping[field_name]
                str_val = str(val).lower() if isinstance(val, bool) else str(val)
                
                stmt = select(AppSetting).where(AppSetting.key == setting_key)
                res = await self.db.execute(stmt)
                existing = res.scalar_one_or_none()
                if existing:
                    existing.value = str_val
                else:
                    new_set = AppSetting(key=setting_key, value=str_val, type=setting_type)
                    self.db.add(new_set)
        
        await self.db.commit()
        return await self.get_preferences()

    async def create_notification(
        self,
        notif_in: NotificationCreate,
        dedup_window_minutes: int = 60
    ) -> Optional[Notification]:
        """
        Cria uma notificação passando por filtros de política, deduplicação e auditoria.
        """
        prefs = await self.get_preferences()
        policy = NotificationPolicy(prefs)

        # 1. Verifica se a origem está habilitada
        if not policy.is_source_enabled(notif_in.source):
            logger.info(f"Notificação descartada: categoria {notif_in.source} desabilitada.")
            return None

        # 2. Gera chave de deduplicação lógica
        # source + source_id + type + window
        dedup_key = f"{notif_in.source}:{notif_in.source_id or 'global'}:{notif_in.type}"
        
        # 3. Deduplicação inteligente
        existing = await self.repo.find_duplicate(dedup_key, within_window_minutes=dedup_window_minutes)
        if existing:
            logger.info(f"Notificação deduplicada ignorada: chave {dedup_key}")
            return existing

        # 4. Cria registro na base de dados
        data_dict = {
            "type": notif_in.type,
            "title": notif_in.title,
            "message": notif_in.message,
            "priority": notif_in.priority.upper(),
            "source": notif_in.source.upper(),
            "source_id": notif_in.source_id,
            "dedup_key": dedup_key,
            "is_read": False,
            "scheduled_for": notif_in.scheduled_for,
            "expires_at": notif_in.expires_at,
            "action_type": notif_in.action_type,
            "action_payload": notif_in.action_payload,
            "requires_confirmation": notif_in.requires_confirmation,
            "status": "PENDING"
        }

        notif = await self.repo.create(data_dict)

        # 5. Auditoria de criação
        audit = ActivityLog(
            type="notification",
            action="notification_created",
            description=f"[{notif.priority}] {notif.title} ({notif.source})",
            metadata_json={"notification_id": notif.id, "source": notif.source}
        )
        self.db.add(audit)
        await self.db.commit()

        # 6. Disparo para canais (Windows Toast / In-App)
        if policy.can_dispatch_toast(notif.priority):
            await dispatcher.dispatch_windows_toast(
                title=notif.title,
                message=notif.message,
                priority=notif.priority,
                action_type=notif.action_type
            )
            audit_sent = ActivityLog(
                type="notification",
                action="notification_sent",
                description=f"Toast enviado via {notif.source}",
                metadata_json={"notification_id": notif.id, "source": notif.source}
            )
            self.db.add(audit_sent)
            await self.db.commit()

        return notif

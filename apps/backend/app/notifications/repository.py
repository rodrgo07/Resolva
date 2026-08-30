from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.notification import Notification
from app.models.settings import AppSetting

class NotificationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, notification_data: Dict[str, Any]) -> Notification:
        # Garante action_data como espelho de action_payload para compatibilidade
        if "action_payload" in notification_data and "action_data" not in notification_data:
            notification_data["action_data"] = notification_data["action_payload"]
        
        notif = Notification(**notification_data)
        self.db.add(notif)
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def get_by_id(self, notif_id: int) -> Optional[Notification]:
        stmt = select(Notification).where(Notification.id == notif_id)
        res = await self.db.execute(stmt)
        return res.scalar_one_or_none()

    async def find_duplicate(self, dedup_key: str, within_window_minutes: int = 60) -> Optional[Notification]:
        if not dedup_key:
            return None
        since = datetime.now() - timedelta(minutes=within_window_minutes)
        stmt = select(Notification).where(
            Notification.dedup_key == dedup_key,
            Notification.created_at >= since,
            Notification.status != "DISMISSED"
        ).order_by(Notification.created_at.desc())
        res = await self.db.execute(stmt)
        return res.scalars().first()

    async def list_notifications(
        self,
        skip: int = 0,
        limit: int = 50,
        unread_only: bool = False,
        source: Optional[str] = None,
        priority: Optional[str] = None,
        include_dismissed: bool = False
    ) -> List[Notification]:
        conditions = []
        if not include_dismissed:
            conditions.append(Notification.status != "DISMISSED")
        if unread_only:
            conditions.append(Notification.is_read == False)
        if source:
            conditions.append(Notification.source == source.upper())
        if priority:
            conditions.append(Notification.priority == priority.upper())

        stmt = select(Notification)
        if conditions:
            stmt = stmt.where(and_(*conditions))
        
        stmt = stmt.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def get_summary(self) -> Dict[str, Any]:
        # Contagem total ativas
        stmt_total = select(func.count(Notification.id)).where(Notification.status != "DISMISSED")
        total_res = await self.db.execute(stmt_total)
        total_count = total_res.scalar() or 0

        # Contagem unread
        stmt_unread = select(func.count(Notification.id)).where(
            Notification.status != "DISMISSED",
            Notification.is_read == False
        )
        unread_res = await self.db.execute(stmt_unread)
        unread_count = unread_res.scalar() or 0

        # Urgent / Critical
        stmt_urgent = select(func.count(Notification.id)).where(
            Notification.status != "DISMISSED",
            Notification.is_read == False,
            Notification.priority.in_(["URGENT", "CRITICAL"])
        )
        urgent_res = await self.db.execute(stmt_urgent)
        urgent_count = urgent_res.scalar() or 0

        # Important
        stmt_important = select(func.count(Notification.id)).where(
            Notification.status != "DISMISSED",
            Notification.is_read == False,
            Notification.priority == "IMPORTANT"
        )
        important_res = await self.db.execute(stmt_important)
        important_count = important_res.scalar() or 0

        # By Source
        stmt_source = select(Notification.source, func.count(Notification.id)).where(
            Notification.status != "DISMISSED",
            Notification.is_read == False
        ).group_by(Notification.source)
        source_res = await self.db.execute(stmt_source)
        by_source = {str(row[0]): row[1] for row in source_res.fetchall()}

        return {
            "unread_count": unread_count,
            "total_count": total_count,
            "urgent_count": urgent_count,
            "important_count": important_count,
            "by_source": by_source
        }

    async def mark_as_read(self, notif_id: int) -> Optional[Notification]:
        notif = await self.get_by_id(notif_id)
        if not notif:
            return None
        notif.is_read = True
        notif.read_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def mark_all_as_read(self) -> int:
        stmt = update(Notification).where(
            Notification.is_read == False,
            Notification.status != "DISMISSED"
        ).values(is_read=True, read_at=datetime.now())
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount or 0

    async def dismiss(self, notif_id: int) -> Optional[Notification]:
        notif = await self.get_by_id(notif_id)
        if not notif:
            return None
        notif.status = "DISMISSED"
        notif.dismissed_at = datetime.now()
        await self.db.commit()
        await self.db.refresh(notif)
        return notif

    async def clean_expired_and_old(self, retention_days: int = 30) -> int:
        now = datetime.now()
        cutoff_date = now - timedelta(days=retention_days)
        
        stmt = delete(Notification).where(
            or_(
                and_(Notification.expires_at.isnot(None), Notification.expires_at <= now),
                and_(Notification.status == "DISMISSED", Notification.created_at <= cutoff_date),
                and_(Notification.is_read == True, Notification.created_at <= cutoff_date)
            )
        )
        res = await self.db.execute(stmt)
        await self.db.commit()
        return res.rowcount or 0

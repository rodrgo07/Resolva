from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import ActivityLog
from typing import Optional, Dict, Any

class ActivityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_activity(self, type: str, action: str, description: str, metadata: Optional[Dict[str, Any]] = None) -> ActivityLog:
        activity = ActivityLog(
            type=type,
            action=action,
            description=description,
            metadata_json=metadata
        )
        self.db.add(activity)
        await self.db.commit()
        await self.db.refresh(activity)
        return activity
        
    async def get_activities(self, skip: int = 0, limit: int = 100):
        from sqlalchemy import select
        query = select(ActivityLog).order_by(ActivityLog.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

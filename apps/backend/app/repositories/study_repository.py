from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta

from app.models.study import StudySubject, StudySession
from app.repositories.base import BaseRepository

class StudyRepository(BaseRepository[StudySubject]):
    def __init__(self, db: AsyncSession):
        super().__init__(StudySubject, db)

    async def get_subjects(self) -> List[StudySubject]:
        return await self.get_all()

    async def create_session(self, data: dict) -> StudySession:
        sess = StudySession(**data)
        self.db.add(sess)
        await self.db.commit()
        await self.db.refresh(sess)
        return sess

    async def get_all_sessions(self, limit: int = 50) -> List[StudySession]:
        query = select(StudySession).order_by(StudySession.started_at.desc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_sessions_by_subject(self, subject_id: int) -> List[StudySession]:
        query = select(StudySession).where(StudySession.subject_id == subject_id)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_study_summary(self) -> Dict[str, Any]:
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        week_start = today_start - timedelta(days=now.weekday())
        month_start = today_start.replace(day=1)
        
        async def get_hours(start_time):
            query = select(func.sum(StudySession.duration_minutes)).where(
                and_(
                    StudySession.started_at >= start_time,
                    StudySession.duration_minutes.is_not(None)
                )
            )
            result = await self.db.execute(query)
            mins = result.scalar() or 0
            return mins / 60.0

        hours_today = await get_hours(today_start)
        hours_this_week = await get_hours(week_start)
        hours_this_month = await get_hours(month_start)
        
        # Simplify by_subject for now
        
        return {
            "hours_today": hours_today,
            "hours_this_week": hours_this_week,
            "hours_this_month": hours_this_month,
            "by_subject": []
        }

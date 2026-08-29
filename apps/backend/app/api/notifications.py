from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.database import get_db
from app.schemas.notification import NotificationResponse
from app.models.notification import Notification
from datetime import datetime

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
async def get_notifications(skip: int = 0, limit: int = 50, db: AsyncSession = Depends(get_db)):
    query = select(Notification).order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())

@router.put("/{id}/read", response_model=NotificationResponse)
async def read_notification(id: int, db: AsyncSession = Depends(get_db)):
    query = update(Notification).where(Notification.id == id).values(
        is_read=True, read_at=datetime.now()
    ).returning(Notification)
    result = await db.execute(query)
    await db.commit()
    return result.scalars().first()

@router.post("/read-all", status_code=200)
async def read_all_notifications(db: AsyncSession = Depends(get_db)):
    query = update(Notification).where(Notification.is_read == False).values(
        is_read=True, read_at=datetime.now()
    )
    await db.execute(query)
    await db.commit()
    return {"message": "All notifications marked as read"}

from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.activity import ActivityResponse
from app.services.activity_service import ActivityService

router = APIRouter()

def get_activity_service(db: AsyncSession = Depends(get_db)) -> ActivityService:
    return ActivityService(db)

@router.get("/", response_model=List[ActivityResponse])
async def get_activities(skip: int = 0, limit: int = 50, service: ActivityService = Depends(get_activity_service)):
    return await service.get_activities(skip, limit)

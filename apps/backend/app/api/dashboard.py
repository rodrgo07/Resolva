from fastapi import APIRouter, Depends, status
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.dashboard_service import DashboardService

router = APIRouter()

def get_dashboard_service(db: AsyncSession = Depends(get_db)) -> DashboardService:
    return DashboardService(db)

@router.get("/overview")
async def get_dashboard_overview(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_overview()

@router.get("/now")
async def get_dashboard_now_card(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_now_card()

@router.get("/timeline")
async def get_dashboard_timeline(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_timeline()

@router.get("/recommendations")
async def get_dashboard_recommendations(service: DashboardService = Depends(get_dashboard_service)):
    return await service.get_recommendations()

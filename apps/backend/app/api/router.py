from fastapi import APIRouter
from app.api import health, tasks, finances, studies, activity, notifications, search, settings

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(finances.router, prefix="/finances", tags=["finances"])
api_router.include_router(studies.router, prefix="/studies", tags=["studies"])
api_router.include_router(activity.router, prefix="/activity", tags=["activity"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])

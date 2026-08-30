from fastapi import APIRouter
from app.api import (
    health, tasks, finances, studies, calendar, emails,
    automations, ai, activity, notifications, search,
    settings, dashboard, backup_sync, devices
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(finances.router, prefix="/finances", tags=["finances"])
api_router.include_router(studies.router, prefix="/studies", tags=["studies"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
api_router.include_router(emails.router, prefix="/emails", tags=["emails"])
api_router.include_router(automations.router, prefix="/automations", tags=["automations"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(activity.router, prefix="/activity", tags=["activity"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(backup_sync.router, tags=["backup_sync"])
api_router.include_router(devices.router, tags=["devices"])


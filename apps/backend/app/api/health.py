from fastapi import APIRouter
from datetime import datetime
from app.__init__ import __version__
import time

router = APIRouter()
startup_time = time.time()

@router.get("/health")
async def health_check():
    uptime = time.time() - startup_time
    return {
        "status": "ok",
        "version": __version__,
        "uptime_seconds": round(uptime, 2),
        "timestamp": datetime.now().isoformat()
    }

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings, validate_production_security
from app.database import engine, Base
import app.models # Garante que todos os modelos estejam importados antes do create_all
from app.api.router import api_router
from app.__init__ import __version__
from app.core.exceptions import ResolvaError, NotFoundError, ValidationError, PermissionError, AutomationSecurityError
from app.core.logging import logger
from app.automation.scheduler import scheduler
from app.notifications.scheduler import notification_scheduler

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Validação de segurança estrita para ambientes de produção (Issue 1)
    validate_production_security()
    
    logger.info("Resolva Backend starting up...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    
    # Inicia schedulers persistentes em background
    try:
        await scheduler.start()
        await notification_scheduler.start()
    except Exception as e:
        logger.warning(f"Não foi possível iniciar os schedulers em background: {e}")

    yield

    logger.info("Resolva Backend shutting down...")
    try:
        await scheduler.stop()
        await notification_scheduler.stop()
    except Exception:
        pass
    await engine.dispose()

app = FastAPI(
    title="Resolva API",
    description="Backend API for Resolva personal management app",
    version=__version__,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(request: Request, exc: NotFoundError):
    logger.warning(f"Resource not found: {exc}")
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": str(exc) or "Recurso não encontrado"}
    )

@app.exception_handler(ValidationError)
async def validation_handler(request: Request, exc: ValidationError):
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": str(exc) or "Dados inválidos"}
    )

@app.exception_handler(PermissionError)
async def permission_handler(request: Request, exc: PermissionError):
    logger.warning(f"Permission denied: {exc}")
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={"detail": str(exc) or "Permissão negada"}
    )

@app.exception_handler(AutomationSecurityError)
async def security_handler(request: Request, exc: AutomationSecurityError):
    logger.error(f"Automation security alert: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc) or "Comando ou ação não autorizada por motivos de segurança"}
    )

@app.exception_handler(ResolvaError)
async def resolva_error_handler(request: Request, exc: ResolvaError):
    logger.error(f"Internal Resolva error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Ocorreu um erro interno no Resolva. Tente novamente mais tarde."}
    )

# Include main router
app.include_router(api_router, prefix="/api")

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True
    )

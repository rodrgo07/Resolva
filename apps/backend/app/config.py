from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional
from pathlib import Path
import os

_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".env"

def _get_database_url() -> str:
    appdata = os.environ.get("APPDATA")
    if appdata:
        resolva_dir = Path(appdata) / "Resolva"
        resolva_dir.mkdir(parents=True, exist_ok=True)
        db_path = resolva_dir / "resolva.db"
        local_db = Path("resolva.db")
        if local_db.exists():
            return f"sqlite+aiosqlite:///{local_db.absolute().as_posix()}"
        return f"sqlite+aiosqlite:///{db_path.as_posix()}"
    return "sqlite+aiosqlite:///./resolva.db"

class Settings(BaseSettings):
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8700
    DATABASE_URL: str = _get_database_url()
    
    AI_PROVIDER: str = "mock"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2048
    
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    ALLOWED_ORIGINS: str = "http://localhost:1420,https://tauri.localhost,http://localhost:5173"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "resolva.log"

    # Google OAuth 2.0 Credentials
    GMAIL_CLIENT_ID: Optional[str] = None
    GMAIL_CLIENT_SECRET: Optional[str] = None

    # Microsoft / Outlook OAuth
    OUTLOOK_CLIENT_ID: Optional[str] = None
    OUTLOOK_CLIENT_SECRET: Optional[str] = None
    OUTLOOK_TENANT_ID: Optional[str] = "common"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

INSECURE_DEFAULT_SECRET_KEYS = {
    "change-this-to-a-random-secret-key",
    "insecure_dev_key",
    "secret",
    "default_secret"
}

def validate_production_security(environment: Optional[str] = None, secret_key: Optional[str] = None) -> bool:
    """
    Valida se a configuração de segurança atende aos requisitos de produção.
    Lança RuntimeError se em produção e a SECRET_KEY for ausente, vazia ou default inseguro.
    NÃO expõe o valor da SECRET_KEY em mensagens de erro ou logs.
    """
    env = (environment or os.getenv("ENVIRONMENT") or getattr(settings, "ENVIRONMENT", "development")).strip().lower()
    
    if env == "production":
        raw_key = secret_key if secret_key is not None else (os.getenv("SECRET_KEY") or getattr(settings, "SECRET_KEY", ""))
        clean_key = raw_key.strip() if isinstance(raw_key, str) else ""

        if not clean_key:
            raise RuntimeError(
                "SECRET_KEY must be explicitly configured with a secure value in production."
            )

        if clean_key in INSECURE_DEFAULT_SECRET_KEYS:
            raise RuntimeError(
                "Insecure default SECRET_KEY detected in production. A secure, unique key is required."
            )

    return True

settings = Settings()


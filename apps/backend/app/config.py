from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent / ".env"

class Settings(BaseSettings):
    BACKEND_HOST: str = "127.0.0.1"
    BACKEND_PORT: int = 8700
    DATABASE_URL: str = "sqlite+aiosqlite:///./resolva.db"
    
    AI_PROVIDER: str = "mock"
    AI_API_KEY: str = ""
    AI_MODEL: str = "gpt-4o-mini"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2048
    
    SECRET_KEY: str = "change-this-to-a-random-secret-key"
    ALLOWED_ORIGINS: str = "http://localhost:1420,https://tauri.localhost,http://localhost:5173"
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "resolva.log"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else None,
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

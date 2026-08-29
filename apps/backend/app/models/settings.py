from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from .base import BaseModel

class AppSetting(BaseModel):
    __tablename__ = "app_settings"

    key: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    value: Mapped[Optional[str]] = mapped_column(String)
    type: Mapped[str] = mapped_column(String(50))

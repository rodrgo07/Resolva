from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import func
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(default=func.now())
    updated_at: Mapped[datetime] = mapped_column(default=func.now(), onupdate=func.now())

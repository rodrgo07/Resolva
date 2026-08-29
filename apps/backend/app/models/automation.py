from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseModel

class Automation(BaseModel):
    __tablename__ = "automations"

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[Optional[str]] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    
    triggers: Mapped[list["AutomationTrigger"]] = relationship(back_populates="automation")
    actions: Mapped[list["AutomationAction"]] = relationship(back_populates="automation")
    executions: Mapped[list["AutomationExecution"]] = relationship(back_populates="automation")

class AutomationTrigger(BaseModel):
    __tablename__ = "automation_triggers"

    automation_id: Mapped[int] = mapped_column(ForeignKey("automations.id"))
    type: Mapped[str] = mapped_column(String(100))
    config: Mapped[Dict[str, Any]] = mapped_column(JSON)
    
    automation: Mapped["Automation"] = relationship(back_populates="triggers")

class AutomationAction(BaseModel):
    __tablename__ = "automation_actions"

    automation_id: Mapped[int] = mapped_column(ForeignKey("automations.id"))
    type: Mapped[str] = mapped_column(String(100))
    config: Mapped[Dict[str, Any]] = mapped_column(JSON)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    
    automation: Mapped["Automation"] = relationship(back_populates="actions")

class AutomationExecution(BaseModel):
    __tablename__ = "automation_executions"

    automation_id: Mapped[int] = mapped_column(ForeignKey("automations.id"))
    status: Mapped[str] = mapped_column(String(50))
    started_at: Mapped[datetime] = mapped_column()
    ended_at: Mapped[Optional[datetime]] = mapped_column()
    log: Mapped[Optional[str]] = mapped_column(String)
    error_message: Mapped[Optional[str]] = mapped_column(String)
    
    automation: Mapped["Automation"] = relationship(back_populates="executions")

from datetime import datetime, date
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Boolean, Integer, Float, DateTime, Date, JSON, Enum as SQLEnum, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class PlanStatus(str, enum.Enum):
    PROPOSED = "PROPOSED"
    APPROVED = "APPROVED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"

class RecommendationFeedbackStatus(str, enum.Enum):
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DISMISSED = "DISMISSED"
    IGNORED = "IGNORED"
    COMPLETED = "COMPLETED"
    PARTIALLY_COMPLETED = "PARTIALLY_COMPLETED"

class AgentPlan(BaseModel):
    __tablename__ = "agent_plans"

    plan_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    plan_date: Mapped[date] = mapped_column(Date, default=date.today, index=True)
    status: Mapped[PlanStatus] = mapped_column(SQLEnum(PlanStatus), default=PlanStatus.PROPOSED, index=True)
    title: Mapped[str] = mapped_column(String(255), default="Plano Diário Otimizado")
    summary: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, default=dict)

    items: Mapped[list["AgentPlanItem"]] = relationship(back_populates="plan", cascade="all, delete-orphan")

class AgentPlanItem(BaseModel):
    __tablename__ = "agent_plan_items"

    plan_id: Mapped[int] = mapped_column(ForeignKey("agent_plans.id", ondelete="CASCADE"), index=True)
    item_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    time_window: Mapped[str] = mapped_column(String(50)) # ex: "09:00 - 11:30"
    activity: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(50), default="deep_work") # deep_work, communication, meeting, study, break
    priority_score: Mapped[float] = mapped_column(Float, default=1.0)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    order_index: Mapped[int] = mapped_column(Integer, default=0)

    plan: Mapped["AgentPlan"] = relationship(back_populates="items")

class AgentRecommendation(BaseModel):
    __tablename__ = "agent_recommendations"

    recommendation_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(100), index=True) # MORNING_PLAN, TASK_WARNING, DEADLINE_WARNING, STUDY_SUGGESTION, etc.
    title: Mapped[str] = mapped_column(String(255))
    explanation: Mapped[str] = mapped_column(String(1000))
    why_reason: Mapped[str] = mapped_column(String(500))
    based_on: Mapped[str] = mapped_column(String(500))
    confidence: Mapped[float] = mapped_column(Float, default=0.85)
    priority: Mapped[str] = mapped_column(String(50), default="medium")
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    suggested_actions: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSON, default=list)

    feedbacks: Mapped[list["AgentRecommendationFeedback"]] = relationship(back_populates="recommendation", cascade="all, delete-orphan")

class AgentRecommendationFeedback(BaseModel):
    __tablename__ = "agent_recommendation_feedbacks"

    recommendation_id: Mapped[int] = mapped_column(ForeignKey("agent_recommendations.id", ondelete="CASCADE"), index=True)
    status: Mapped[RecommendationFeedbackStatus] = mapped_column(SQLEnum(RecommendationFeedbackStatus), default=RecommendationFeedbackStatus.ACCEPTED)
    user_comment: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    recommendation: Mapped["AgentRecommendation"] = relationship(back_populates="feedbacks")

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date

class PlanItemSchema(BaseModel):
    item_id: str
    time_window: str
    activity: str
    category: str = "deep_work"
    priority_score: float = 1.0
    is_completed: bool = False
    order_index: int = 0

    model_config = ConfigDict(from_attributes=True)

class AgentPlanResponse(BaseModel):
    plan_id: str
    plan_date: date
    status: str
    title: str
    summary: Optional[str] = None
    items: List[PlanItemSchema] = []

    model_config = ConfigDict(from_attributes=True)

class AgentPlanCreateRequest(BaseModel):
    title: Optional[str] = "Plano Diário Otimizado"
    plan_date: Optional[date] = None
    summary: Optional[str] = None

class RecommendationResponse(BaseModel):
    recommendation_id: str
    category: str
    title: str
    explanation: str
    why_reason: str
    based_on: str
    confidence: float
    priority: str
    expires_at: datetime
    suggested_actions: List[Dict[str, Any]] = []

    model_config = ConfigDict(from_attributes=True)

class RecommendationFeedbackRequest(BaseModel):
    status: str = Field("ACCEPTED", description="ACCEPTED, REJECTED, DISMISSED, IGNORED, COMPLETED, PARTIALLY_COMPLETED")
    user_comment: Optional[str] = None

class WeeklyReviewResponse(BaseModel):
    start_date: date
    end_date: date
    completed_tasks_count: int
    overdue_tasks_count: int
    completion_rate_pct: float
    total_focus_hours: float
    pomodoro_sessions_count: int
    total_expenses: float
    events_attended_count: int
    detected_patterns: List[str] = []
    insights_and_recommendations: List[str] = []

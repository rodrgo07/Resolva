from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class OrchestrationRun(Base):
    __tablename__ = "orchestration_runs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    run_id = Column(String(100), unique=True, index=True, nullable=False)
    status = Column(String(50), default="RUNNING", index=True, nullable=False) # RUNNING, WAITING_CONFIRMATION, COMPLETED, FAILED, CANCELLED
    trigger_type = Column(String(50), default="MANUAL", nullable=False) # MANUAL, EVENT, SCHEDULE, AGENT, RECOVERY
    trigger_source = Column(String(100), default="USER", nullable=False)
    device_id = Column(String(100), default="DESKTOP-MAIN", nullable=False)
    correlation_id = Column(String(100), index=True, nullable=True)
    idempotency_key = Column(String(100), unique=True, nullable=True)
    is_dry_run = Column(Boolean, default=False, nullable=False)
    total_steps = Column(Integer, default=0, nullable=False)
    completed_steps = Column(Integer, default=0, nullable=False)
    error = Column(Text, nullable=True)
    plan_snapshot = Column(JSON, nullable=False, default=list) # List of planned workflows / steps
    context_snapshot = Column(JSON, nullable=False, default=dict)
    metrics = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    explanations = relationship("WorkflowExplanationModel", back_populates="orchestration_run", cascade="all, delete-orphan")
    feedbacks = relationship("WorkflowFeedbackModel", back_populates="orchestration_run", cascade="all, delete-orphan")

class WorkflowEventRule(Base):
    __tablename__ = "workflow_event_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rule_id = Column(String(100), unique=True, index=True, nullable=False)
    event_type = Column(String(100), index=True, nullable=False) # TASK_OVERDUE, POMODORO_COMPLETED, etc.
    workflow_id = Column(String(100), index=True, nullable=False)
    name = Column(String(255), nullable=False)
    conditions = Column(JSON, nullable=True, default=dict)
    cooldown_seconds = Column(Integer, default=300, nullable=False)
    priority = Column(String(20), default="NORMAL", nullable=False) # LOW, NORMAL, HIGH, URGENT
    requires_confirmation = Column(Boolean, default=False, nullable=False)
    enabled = Column(Boolean, default=True, index=True, nullable=False)
    last_triggered_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class WorkflowDependency(Base):
    __tablename__ = "workflow_dependencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    dependency_id = Column(String(100), unique=True, index=True, nullable=False)
    parent_workflow_id = Column(String(100), index=True, nullable=False)
    child_workflow_id = Column(String(100), index=True, nullable=False)
    on_failure_policy = Column(String(50), default="FAIL_FAST", nullable=False) # FAIL_FAST, CONTINUE, RETRY, SKIP_DEPENDENTS, ASK_USER
    condition = Column(JSON, nullable=True, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class WorkflowFeedbackModel(Base):
    __tablename__ = "workflow_feedbacks"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    feedback_id = Column(String(100), unique=True, index=True, nullable=False)
    orchestration_run_id = Column(String(100), ForeignKey("orchestration_runs.run_id", ondelete="CASCADE"), nullable=True)
    workflow_id = Column(String(100), index=True, nullable=False)
    action_type = Column(String(100), nullable=True)
    user_action = Column(String(50), nullable=False) # ACCEPTED, REJECTED, DISMISSED, IGNORED, CANCELLED
    reason = Column(String(255), nullable=True)
    device_id = Column(String(100), default="DESKTOP-MAIN", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    orchestration_run = relationship("OrchestrationRun", back_populates="feedbacks")

class WorkflowExplanationModel(Base):
    __tablename__ = "workflow_explanations"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    explanation_id = Column(String(100), unique=True, index=True, nullable=False)
    orchestration_run_id = Column(String(100), ForeignKey("orchestration_runs.run_id", ondelete="CASCADE"), nullable=True)
    workflow_id = Column(String(100), index=True, nullable=False)
    title = Column(String(255), nullable=False)
    reason = Column(Text, nullable=False)
    factors = Column(JSON, nullable=False, default=list) # List of rationale bullet points
    confidence = Column(Integer, default=85, nullable=False)
    source_data = Column(JSON, nullable=True, default=dict)
    generated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    orchestration_run = relationship("OrchestrationRun", back_populates="explanations")

from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import String, Boolean, Integer, ForeignKey, JSON, DateTime, Text, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from .base import BaseModel

class WorkflowStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    RUNNING = "RUNNING"
    WAITING_CONFIRMATION = "WAITING_CONFIRMATION"
    WAITING_CONDITION = "WAITING_CONDITION"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DISABLED = "DISABLED"

class WorkflowSafetyLevel(str, enum.Enum):
    MANUAL_ONLY = "MANUAL_ONLY"
    SUGGEST_ONLY = "SUGGEST_ONLY"
    AUTO_LOW_RISK = "AUTO_LOW_RISK"
    AUTO_WITH_CONFIRMATION = "AUTO_WITH_CONFIRMATION"
    DISABLED = "DISABLED"

class WorkflowExecutionPolicy(str, enum.Enum):
    ALLOW_PARALLEL = "ALLOW_PARALLEL"
    SINGLE_ACTIVE = "SINGLE_ACTIVE"
    QUEUE = "QUEUE"
    SKIP_IF_RUNNING = "SKIP_IF_RUNNING"

class Workflow(BaseModel):
    __tablename__ = "workflows"

    workflow_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE", index=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_by: Mapped[str] = mapped_column(String(100), default="USER") # USER, AGENT, TEMPLATE
    safety_level: Mapped[str] = mapped_column(String(50), default="AUTO_LOW_RISK")
    execution_policy: Mapped[str] = mapped_column(String(50), default="SINGLE_ACTIVE")
    max_runtime_seconds: Mapped[int] = mapped_column(Integer, default=300)
    priority: Mapped[str] = mapped_column(String(20), default="NORMAL") # LOW, NORMAL, HIGH, CRITICAL
    
    # Declarative configurations
    trigger_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    condition_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    action_config: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    retry_policy: Mapped[Dict[str, Any]] = mapped_column(JSON, default=lambda: {"max_attempts": 3, "backoff": [5, 15, 30]})
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, default=list)

    steps: Mapped[List["WorkflowStep"]] = relationship(back_populates="workflow", cascade="all, delete-orphan", order_by="WorkflowStep.order")
    executions: Mapped[List["WorkflowExecution"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")

class WorkflowStep(BaseModel):
    __tablename__ = "workflow_steps"

    step_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(100), ForeignKey("workflows.workflow_id"), index=True)
    order: Mapped[int] = mapped_column(Integer, default=1)
    name: Mapped[str] = mapped_column(String(255))
    action_type: Mapped[str] = mapped_column(String(100), index=True) # Homologated Catalog
    parameters: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    condition: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(Integer, default=60)
    retry_policy: Mapped[Dict[str, Any]] = mapped_column(JSON, default=lambda: {"max_attempts": 2, "backoff": [3, 10]})
    permission_level: Mapped[str] = mapped_column(String(50), default="LOW")
    requires_confirmation: Mapped[bool] = mapped_column(Boolean, default=False)
    compensating_action: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="steps")

class WorkflowExecution(BaseModel):
    __tablename__ = "workflow_executions"

    execution_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    workflow_id: Mapped[str] = mapped_column(String(100), ForeignKey("workflows.workflow_id"), index=True)
    workflow_version: Mapped[int] = mapped_column(Integer, default=1)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="RUNNING", index=True) # RUNNING, COMPLETED, FAILED, WAITING_CONFIRMATION, CANCELLED, PARTIAL_FAILURE, TIMEOUT
    current_step_order: Mapped[int] = mapped_column(Integer, default=1)
    trigger_source: Mapped[str] = mapped_column(String(100), default="MANUAL")
    device_id: Mapped[str] = mapped_column(String(100), default="DESKTOP-MAIN")
    correlation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    is_dry_run: Mapped[bool] = mapped_column(Boolean, default=False)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    result_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    workflow: Mapped["Workflow"] = relationship(back_populates="executions")
    step_executions: Mapped[List["WorkflowStepExecution"]] = relationship(back_populates="execution", cascade="all, delete-orphan")
    confirmations: Mapped[List["WorkflowConfirmation"]] = relationship(back_populates="execution", cascade="all, delete-orphan")

class WorkflowStepExecution(BaseModel):
    __tablename__ = "workflow_step_executions"

    step_execution_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    execution_id: Mapped[str] = mapped_column(String(100), ForeignKey("workflow_executions.execution_id"), index=True)
    step_id: Mapped[str] = mapped_column(String(100), index=True)
    step_order: Mapped[int] = mapped_column(Integer, default=1)
    action_type: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # PENDING, RUNNING, COMPLETED, FAILED, SKIPPED, WAITING_CONFIRMATION
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    finished_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)
    result: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    execution: Mapped["WorkflowExecution"] = relationship(back_populates="step_executions")

class WorkflowConfirmation(BaseModel):
    __tablename__ = "workflow_confirmations"

    confirmation_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    execution_id: Mapped[str] = mapped_column(String(100), ForeignKey("workflow_executions.execution_id"), index=True)
    step_id: Mapped[str] = mapped_column(String(100))
    action_type: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(String(255))
    parameters_summary: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    risk_level: Mapped[str] = mapped_column(String(50), default="MEDIUM")
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # PENDING, APPROVED, REJECTED, EXPIRED
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    device_id: Mapped[str] = mapped_column(String(100), default="DESKTOP-MAIN")
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    resolved_by_device: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    execution: Mapped["WorkflowExecution"] = relationship(back_populates="confirmations")

class WorkflowRecommendation(BaseModel):
    __tablename__ = "workflow_recommendations"

    recommendation_id: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    reason: Mapped[str] = mapped_column(String(255))
    suggested_workflow: Mapped[Dict[str, Any]] = mapped_column(JSON)
    confidence: Mapped[int] = mapped_column(Integer, default=85)
    status: Mapped[str] = mapped_column(String(50), default="PENDING") # PENDING, ACCEPTED, DISMISSED
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

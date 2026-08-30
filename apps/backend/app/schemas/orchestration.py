from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

# ========================================================
# 1. ORCHESTRATION CANDIDATE & SCORING
# ========================================================

class WorkflowCandidate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    workflow_id: str
    name: str
    score: float
    confidence: int = 85
    priority: str = "NORMAL"
    required_confirmation: bool = False
    estimated_duration_seconds: int = 60
    expected_outcome: str
    reason: str
    factors: List[str] = Field(default_factory=list)
    action_preview: List[str] = Field(default_factory=list)

class WorkflowExplanationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    explanation_id: str
    workflow_id: str
    title: str
    reason: str
    factors: List[str] = Field(default_factory=list)
    confidence: int
    source_data: Optional[Dict[str, Any]] = None
    generated_at: datetime

# ========================================================
# 2. ORCHESTRATION RUNS & CHAINS
# ========================================================

class OrchestrationStepPlan(BaseModel):
    step_order: int
    workflow_id: str
    workflow_name: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    permission_level: str = "LOW"
    requires_confirmation: bool = False
    on_failure_policy: str = "FAIL_FAST" # FAIL_FAST, CONTINUE, RETRY, SKIP_DEPENDENTS

class OrchestrationRunRequest(BaseModel):
    trigger_type: str = "MANUAL" # MANUAL, EVENT, SCHEDULE, AGENT, PLAN
    trigger_source: str = "USER"
    device_id: str = "DESKTOP-MAIN"
    is_dry_run: bool = False
    idempotency_key: Optional[str] = None
    workflow_ids: Optional[List[str]] = None
    chain_mode: bool = True
    context_override: Optional[Dict[str, Any]] = None

class OrchestrationRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_id: str
    status: str
    trigger_type: str
    trigger_source: str
    device_id: str
    correlation_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    is_dry_run: bool
    total_steps: int
    completed_steps: int
    error: Optional[str] = None
    plan_snapshot: List[Dict[str, Any]] = Field(default_factory=list)
    context_snapshot: Dict[str, Any] = Field(default_factory=dict)
    metrics: Optional[Dict[str, Any]] = None
    created_at: datetime
    finished_at: Optional[datetime] = None
    updated_at: datetime

# ========================================================
# 3. EVENT RULES & DEPENDENCIES
# ========================================================

class WorkflowEventRuleCreate(BaseModel):
    name: str
    event_type: str
    workflow_id: str
    conditions: Optional[Dict[str, Any]] = Field(default_factory=dict)
    cooldown_seconds: int = 300
    priority: str = "NORMAL"
    requires_confirmation: bool = False
    enabled: bool = True

class WorkflowEventRuleResponse(WorkflowEventRuleCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    rule_id: str
    last_triggered_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class WorkflowDependencyCreate(BaseModel):
    parent_workflow_id: str
    child_workflow_id: str
    on_failure_policy: str = "FAIL_FAST"
    condition: Optional[Dict[str, Any]] = Field(default_factory=dict)

class WorkflowDependencyResponse(WorkflowDependencyCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dependency_id: str
    created_at: datetime

# ========================================================
# 4. FEEDBACK & METRICS
# ========================================================

class WorkflowFeedbackCreate(BaseModel):
    workflow_id: str
    orchestration_run_id: Optional[str] = None
    action_type: Optional[str] = None
    user_action: str # ACCEPTED, REJECTED, DISMISSED, IGNORED, CANCELLED
    reason: Optional[str] = None
    device_id: str = "DESKTOP-MAIN"

class WorkflowFeedbackResponse(WorkflowFeedbackCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    feedback_id: str
    created_at: datetime

class OrchestrationMetricsResponse(BaseModel):
    total_orchestrations: int
    completed_runs: int
    failed_runs: int
    waiting_confirmations: int
    avg_duration_seconds: float
    retry_rate_percent: float
    confirmation_acceptance_rate: float
    most_triggered_workflows: List[Dict[str, Any]]

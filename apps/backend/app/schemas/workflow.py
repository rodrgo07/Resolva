from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ========================================================
# WORKFLOW SCHEMAS
# ========================================================

class WorkflowStepCreate(BaseModel):
    name: str
    action_type: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    condition: Optional[Dict[str, Any]] = None
    timeout_seconds: int = 60
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_attempts": 2, "backoff": [3, 10]})
    permission_level: str = "LOW"
    requires_confirmation: bool = False
    compensating_action: Optional[str] = None

class WorkflowStepResponse(WorkflowStepCreate):
    id: int
    step_id: str
    workflow_id: str
    order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool = True
    safety_level: str = "AUTO_LOW_RISK"
    execution_policy: str = "SINGLE_ACTIVE"
    max_runtime_seconds: int = 300
    priority: str = "NORMAL"
    trigger_config: Dict[str, Any] = Field(default_factory=dict)
    condition_config: Optional[Dict[str, Any]] = None
    action_config: Optional[Dict[str, Any]] = None
    retry_policy: Dict[str, Any] = Field(default_factory=lambda: {"max_attempts": 3, "backoff": [5, 15, 30]})
    tags: List[str] = Field(default_factory=list)
    steps: List[WorkflowStepCreate] = Field(default_factory=list)

class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    enabled: Optional[bool] = None
    status: Optional[str] = None
    safety_level: Optional[str] = None
    execution_policy: Optional[str] = None
    max_runtime_seconds: Optional[int] = None
    priority: Optional[str] = None
    trigger_config: Optional[Dict[str, Any]] = None
    condition_config: Optional[Dict[str, Any]] = None
    retry_policy: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    steps: Optional[List[WorkflowStepCreate]] = None

class WorkflowResponse(BaseModel):
    id: int
    workflow_id: str
    name: str
    description: Optional[str]
    enabled: bool
    status: str
    version: int
    created_by: str
    safety_level: str
    execution_policy: str
    max_runtime_seconds: int
    priority: str
    trigger_config: Dict[str, Any]
    condition_config: Optional[Dict[str, Any]]
    action_config: Optional[Dict[str, Any]]
    retry_policy: Dict[str, Any]
    tags: Optional[List[str]]
    steps: List[WorkflowStepResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# ========================================================
# EXECUTION & CONFIRMATION SCHEMAS
# ========================================================

class WorkflowStepExecutionResponse(BaseModel):
    id: int
    step_execution_id: str
    execution_id: str
    step_id: str
    step_order: int
    action_type: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    retry_count: int
    result: Optional[Dict[str, Any]]
    error: Optional[str]

    class Config:
        from_attributes = True

class WorkflowConfirmationResponse(BaseModel):
    id: int
    confirmation_id: str
    execution_id: str
    step_id: str
    action_type: str
    description: str
    parameters_summary: Dict[str, Any]
    risk_level: str
    status: str
    expires_at: datetime
    device_id: str
    resolved_at: Optional[datetime]
    resolved_by_device: Optional[str]

    class Config:
        from_attributes = True

class WorkflowExecutionResponse(BaseModel):
    id: int
    execution_id: str
    workflow_id: str
    workflow_version: int
    started_at: datetime
    finished_at: Optional[datetime]
    status: str
    current_step_order: int
    trigger_source: str
    device_id: str
    correlation_id: Optional[str]
    is_dry_run: bool
    error: Optional[str]
    result_summary: Optional[Dict[str, Any]]
    step_executions: List[WorkflowStepExecutionResponse] = Field(default_factory=list)
    confirmations: List[WorkflowConfirmationResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class WorkflowConfirmationRequest(BaseModel):
    approved: bool
    device_id: str = "DESKTOP-MAIN"
    reason: Optional[str] = None

class WorkflowExecuteRequest(BaseModel):
    device_id: str = "DESKTOP-MAIN"
    trigger_source: str = "MANUAL"
    dry_run: bool = False
    context_override: Optional[Dict[str, Any]] = None

class WorkflowRecommendationResponse(BaseModel):
    id: int
    recommendation_id: str
    title: str
    description: str
    reason: str
    suggested_workflow: Dict[str, Any]
    confidence: int
    status: str
    created_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True

class WorkflowTemplateResponse(BaseModel):
    template_id: str
    name: str
    description: str
    category: str
    safety_level: str
    trigger_config: Dict[str, Any]
    condition_config: Optional[Dict[str, Any]]
    steps: List[WorkflowStepCreate]

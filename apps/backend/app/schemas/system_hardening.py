from pydantic import BaseModel, Field, ConfigDict
from typing import List, Dict, Any, Optional
from datetime import datetime

# ========================================================
# 1. SYSTEM HEALTH & DIAGNOSTICS
# ========================================================

class ComponentHealth(BaseModel):
    component: str
    status: str # HEALTHY, DEGRADED, WARNING, CRITICAL, OFFLINE
    timestamp: datetime
    latency_ms: float
    message: str
    details: Dict[str, Any] = Field(default_factory=dict)
    recoverable: bool = True
    recommended_action: Optional[str] = None

class DiagnosticItem(BaseModel):
    code: str
    level: str # INFO, WARNING, ERROR, CRITICAL
    component: str
    message: str
    timestamp: datetime
    details: Optional[Dict[str, Any]] = None

class SystemHealthResponse(BaseModel):
    check_id: str
    overall_status: str # HEALTHY, DEGRADED, WARNING, CRITICAL, OFFLINE
    safe_mode_active: bool
    components: Dict[str, ComponentHealth]
    diagnostics: List[DiagnosticItem]
    metrics_summary: Dict[str, Any]
    checked_at: datetime

# ========================================================
# 2. SAFETY & AUTONOMY POLICIES
# ========================================================

class SafetyPolicyState(BaseModel):
    global_safe_mode: bool = False
    automations_enabled: bool = True
    orchestration_enabled: bool = True
    remote_control_enabled: bool = True
    agent_actions_enabled: bool = True
    notifications_enabled: bool = True
    autonomy_level: str = "LEVEL_3_LOW_RISK_AUTO"
    updated_at: datetime

class SafetyPolicyUpdateRequest(BaseModel):
    global_safe_mode: Optional[bool] = None
    automations_enabled: Optional[bool] = None
    orchestration_enabled: Optional[bool] = None
    remote_control_enabled: Optional[bool] = None
    agent_actions_enabled: Optional[bool] = None
    notifications_enabled: Optional[bool] = None
    autonomy_level: Optional[str] = None

# ========================================================
# 3. AUDIT LOGS & TRACING
# ========================================================

class AuditEventCreate(BaseModel):
    source: str = "SYSTEM"
    device_id: str = "DESKTOP-MAIN"
    actor: str = "USER"
    action: str
    risk: str = "LOW"
    status: str = "SUCCESS"
    reason: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None

class AuditEventResponse(AuditEventCreate):
    model_config = ConfigDict(from_attributes=True)

    id: int
    audit_id: str
    timestamp: datetime

# ========================================================
# 4. SYSTEM METRICS & RELEASE READINESS
# ========================================================

class SystemMetricsResponse(BaseModel):
    uptime_seconds: float
    api_latency_ms: float
    database_latency_ms: float
    websocket_latency_ms: float
    active_devices_count: int
    sync_queue_depth: int
    total_audit_events: int
    total_orchestrations: int
    failed_actions_rate: float
    safe_mode: bool
    memory_usage_mb: float

class ReleaseCheckItem(BaseModel):
    name: str
    status: str # PASS, WARN, FAIL
    message: str
    is_blocking: bool

class ReleaseReadinessResponse(BaseModel):
    status: str # READY, NOT_READY
    overall_score: int
    checks: List[ReleaseCheckItem]
    blocking_errors: List[str]
    warnings: List[str]
    checked_at: datetime

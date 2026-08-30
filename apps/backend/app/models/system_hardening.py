from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text, Float
from datetime import datetime
from app.database import Base

class SystemHealthRecord(Base):
    __tablename__ = "system_health_records"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    check_id = Column(String(100), unique=True, index=True, nullable=False)
    overall_status = Column(String(50), default="HEALTHY", nullable=False) # HEALTHY, DEGRADED, WARNING, CRITICAL, OFFLINE
    safe_mode_active = Column(Boolean, default=False, nullable=False)
    components_status = Column(JSON, nullable=False, default=dict)
    diagnostics = Column(JSON, nullable=False, default=list)
    metrics_summary = Column(JSON, nullable=True, default=dict)
    checked_at = Column(DateTime, default=datetime.utcnow, nullable=False)

class SafetyPolicySetting(Base):
    __tablename__ = "safety_policy_settings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    enabled = Column(Boolean, default=True, nullable=False)
    autonomy_level = Column(String(50), default="LEVEL_3_LOW_RISK_AUTO", nullable=False)
    description = Column(String(255), nullable=True)
    config = Column(JSON, nullable=True, default=dict)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class AuditEventLog(Base):
    __tablename__ = "audit_event_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    audit_id = Column(String(100), unique=True, index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True, nullable=False)
    source = Column(String(100), default="SYSTEM", nullable=False) # DESKTOP, MOBILE, AGENT, WORKFLOW, ORCHESTRATION
    device_id = Column(String(100), default="DESKTOP-MAIN", nullable=False)
    actor = Column(String(100), default="USER", nullable=False)
    action = Column(String(100), nullable=False)
    risk = Column(String(50), default="LOW", nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    status = Column(String(50), default="SUCCESS", nullable=False) # SUCCESS, BLOCKED, FAILED, CONFIRMED, REJECTED
    reason = Column(String(255), nullable=True)
    details = Column(JSON, nullable=True, default=dict)
    correlation_id = Column(String(100), index=True, nullable=True)
    trace_id = Column(String(100), index=True, nullable=True)

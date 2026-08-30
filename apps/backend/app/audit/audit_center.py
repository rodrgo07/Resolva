import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.system_hardening import AuditEventLog
from app.system.logging import structured_logger

class AuditCenter:
    """
    Central de Auditoria Completa e Imutável do RESOLVA (Fase 35).
    Registra logins, comandos remotos, orquestrações, confirmações e violações de segurança.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_event(
        self,
        action: str,
        source: str = "SYSTEM",
        device_id: str = "DESKTOP-MAIN",
        actor: str = "USER",
        risk: str = "LOW",
        status: str = "SUCCESS",
        reason: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None
    ) -> AuditEventLog:
        # 1. Sanitização de Segredos
        sanitized_details = structured_logger.sanitize(details or {})

        audit_id = f"aud_{uuid.uuid4().hex[:10]}"
        event = AuditEventLog(
            audit_id=audit_id,
            timestamp=datetime.utcnow(),
            source=source,
            device_id=device_id,
            actor=actor,
            action=action,
            risk=risk,
            status=status,
            reason=reason,
            details=sanitized_details,
            correlation_id=correlation_id,
            trace_id=trace_id
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        # Log estruturado simultâneo
        structured_logger.log(
            level="INFO" if status == "SUCCESS" else "WARNING",
            component="AUDIT_CENTER",
            event=action,
            message=f"[{actor}] {action} - Status: {status}",
            correlation_id=correlation_id,
            device_id=device_id,
            details=sanitized_details
        )
        return event

    async def list_audit_events(self, limit: int = 50) -> List[AuditEventLog]:
        stmt = select(AuditEventLog).order_by(desc(AuditEventLog.timestamp)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

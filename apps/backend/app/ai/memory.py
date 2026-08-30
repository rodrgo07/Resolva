import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy import select, delete, update, and_, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_memory import AgentMemoryItem, MemoryType, MemoryStatus
from app.models.activity import ActivityLog
from app.models.task import Task
from app.models.finance import Expense
from app.models.study import StudySession
from app.core.exceptions import NotFoundError, ValidationError

class AgentMemoryManager:
    """
    Fase 31: MemoryEngine & Episodic Context.
    Gerencia:
    - Memórias Estruturadas (FACT, PREFERENCE, ROUTINE, BEHAVIOR, DECISION, OUTCOME)
    - Níveis de Confiança (0.0 a 1.0)
    - Expiração e Invalidação
    - Auditoria de Atividades
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_memory(
        self,
        content: str,
        type: str = "FACT",
        source: str = "USER_EXPLICIT",
        confidence: float = 0.90,
        importance: int = 3,
        expires_at: Optional[datetime] = None
    ) -> AgentMemoryItem:
        # Sanitização de segurança estrita: bloqueia credenciais
        content_lower = content.lower()
        if any(w in content_lower for w in ["password", "senha", "bearer", "oauth_token", "secret_key"]):
            raise ValidationError("Conteúdo contém termos sensíveis e não pode ser persistido na memória.")

        # Evita duplicações
        stmt = select(AgentMemoryItem).where(
            AgentMemoryItem.content == content.strip(),
            AgentMemoryItem.status == MemoryStatus.ACTIVE
        )
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            existing.confidence = max(existing.confidence, confidence)
            existing.last_used_at = datetime.utcnow()
            await self.db.commit()
            return existing

        mem_id = f"mem_{uuid.uuid4().hex[:8]}"
        item = AgentMemoryItem(
            memory_id=mem_id,
            type=MemoryType(type.upper()) if type.upper() in MemoryType.__members__ else MemoryType.FACT,
            content=content.strip(),
            source=source,
            confidence=min(1.0, max(0.0, confidence)),
            importance=min(5, max(1, importance)),
            status=MemoryStatus.ACTIVE,
            expires_at=expires_at,
            last_used_at=datetime.utcnow()
        )
        self.db.add(item)
        await self.db.commit()
        return item

    async def list_memories(
        self,
        type: Optional[str] = None,
        query: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[AgentMemoryItem]:
        stmt = select(AgentMemoryItem).where(AgentMemoryItem.status == MemoryStatus.ACTIVE)
        if type:
            stmt = stmt.where(AgentMemoryItem.type == MemoryType(type.upper()))
        if query:
            stmt = stmt.where(AgentMemoryItem.content.ilike(f"%{query}%"))
        if min_confidence > 0.0:
            stmt = stmt.where(AgentMemoryItem.confidence >= min_confidence)
            
        stmt = stmt.order_by(AgentMemoryItem.importance.desc(), AgentMemoryItem.confidence.desc())
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def update_memory(
        self,
        memory_id: str,
        content: Optional[str] = None,
        confidence: Optional[float] = None,
        importance: Optional[int] = None,
        status: Optional[str] = None
    ) -> AgentMemoryItem:
        stmt = select(AgentMemoryItem).where(AgentMemoryItem.memory_id == memory_id)
        res = await self.db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            raise NotFoundError("Memória não encontrada.")

        if content is not None:
            content_lower = content.lower()
            if any(w in content_lower for w in ["password", "senha", "bearer", "oauth_token", "secret_key"]):
                raise ValidationError("Conteúdo contém termos sensíveis e não pode ser persistido na memória.")
            item.content = content.strip()

        if confidence is not None:
            item.confidence = min(1.0, max(0.0, confidence))

        if importance is not None:
            item.importance = min(5, max(1, importance))

        if status is not None and status.upper() in MemoryStatus.__members__:
            item.status = MemoryStatus(status.upper())

        item.last_used_at = datetime.utcnow()
        await self.db.commit()
        return item

    async def delete_memory(self, memory_id: str) -> None:
        stmt = select(AgentMemoryItem).where(AgentMemoryItem.memory_id == memory_id)
        res = await self.db.execute(stmt)
        item = res.scalar_one_or_none()
        if not item:
            raise NotFoundError("Memória não encontrada.")
        await self.db.delete(item)
        await self.db.commit()

    async def clear_all_memories(self) -> None:
        await self.db.execute(delete(AgentMemoryItem))
        await self.db.execute(delete(ActivityLog).where(ActivityLog.type == "agent"))
        await self.db.commit()

    async def log_agent_activity(
        self,
        tool_name: str,
        description: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        meta = metadata or {}
        sanitized_meta = {}
        for k, v in meta.items():
            if "token" not in str(k).lower() and "secret" not in str(k).lower() and "password" not in str(k).lower():
                if isinstance(v, (str, int, float, bool, list, dict)) or v is None:
                    sanitized_meta[str(k)] = v
                else:
                    sanitized_meta[str(k)] = str(v)
                    
        sanitized_meta["tool_name"] = tool_name
        sanitized_meta["status"] = status

        log = ActivityLog(
            type="agent",
            action=f"Agent: {tool_name}",
            description=description,
            metadata_json=sanitized_meta
        )
        self.db.add(log)
        await self.db.commit()

    async def get_user_behavioral_patterns(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        thirty_days_ago = now - timedelta(days=30)

        # Taxa de conclusão de tarefas
        stmt_comp = select(func.count(Task.id)).where(Task.status == "concluida", Task.updated_at >= thirty_days_ago)
        res_comp = await self.db.execute(stmt_comp)
        completed_count = res_comp.scalar() or 0

        # Média diária de foco/estudo (minutos)
        stmt_study = select(func.sum(StudySession.duration_minutes)).where(StudySession.started_at >= thirty_days_ago)
        res_study = await self.db.execute(stmt_study)
        total_focus_min = res_study.scalar() or 0

        # Despesas recentes
        stmt_exp = select(func.sum(Expense.amount)).where(Expense.date >= (now - timedelta(days=30)).date())
        res_exp = await self.db.execute(stmt_exp)
        total_exp = res_exp.scalar() or 0.0

        # Memórias ativas
        memories = await self.list_memories(min_confidence=0.5)

        return {
            "completed_tasks_last_30d": completed_count,
            "total_focus_minutes_last_30d": total_focus_min,
            "total_expenses_last_30d": float(total_exp),
            "estimated_focus_peak_hours": "09:00 - 11:30",
            "preferred_study_mode": "Pomodoro (25m)",
            "contextual_memories_count": len(memories)
        }

    async def get_recent_activities(self, limit: int = 15) -> List[Dict[str, Any]]:
        stmt = select(ActivityLog).where(ActivityLog.type == "agent").order_by(ActivityLog.created_at.desc()).limit(limit)
        res = await self.db.execute(stmt)
        logs = res.scalars().all()
        return [
            {
                "id": l.id,
                "action": l.action,
                "description": l.description,
                "timestamp": l.created_at.strftime("%d/%m %H:%M"),
                "metadata_info": l.metadata_json if isinstance(l.metadata_json, dict) else {}
            }
            for l in logs
        ]

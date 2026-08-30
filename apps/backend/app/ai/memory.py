from typing import List, Dict, Any, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.activity import ActivityLog

class AgentMemoryManager:
    """
    Gerencia memórias e contexto do Resolva Agent:
    - CONVERSATION_MEMORY: histórico de mensagens
    - USER_PREFERENCES / TASK_CONTEXT: dados estruturados
    - AUDIT: histórico de atividades executadas pelo Agent
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def log_agent_activity(
        self,
        tool_name: str,
        description: str,
        status: str = "success",
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Registra auditoria de ações do Agent (sem tokens, sem objetos complexos)"""
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
            metadata=sanitized_meta
        )
        self.db.add(log)
        await self.db.commit()

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
                "metadata_info": l.metadata if isinstance(l.metadata, dict) else {}
            }
            for l in logs
        ]

    async def clear_all_memories(self) -> None:
        """Permite ao usuário apagar todas as memórias e logs do Agent"""
        await self.db.execute(delete(ActivityLog).where(ActivityLog.type == "agent"))
        await self.db.commit()

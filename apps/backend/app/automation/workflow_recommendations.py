import uuid
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from app.models.workflow import WorkflowRecommendation
from app.ai.pattern_engine import PatternEngine
from app.services.event_bus import event_bus

class WorkflowRecommendationsEngine:
    """
    Motor Proativo de Sugestões de Workflows (Fase 33).
    Analisa padrões de produtividade e gera sugestões declarativas de automação.
    NUNCA ativa automações silenciosamente sem consentimento explícito do usuário.
    """
    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_recommendations(self) -> List[WorkflowRecommendation]:
        pattern_eng = PatternEngine(self.db)
        patterns = await pattern_eng.analyze_productivity_patterns()

        recommendations = []

        # 1. Recomendação de Estudo Noturno baseado em hábitos
        if patterns.get("best_focus_window") or patterns.get("detected_habits"):
            rec_id = f"wrec_{uuid.uuid4().hex[:8]}"
            rec = WorkflowRecommendation(
                recommendation_id=rec_id,
                title="Automação Sugerida: Início de Estudo às 19h",
                description="Percebemos que você costuma ter blocos de foco no período noturno. Deseja criar uma automação para iniciar seu Pomodoro automaticamente?",
                reason="Padrão consistente de sessões de estudo detectado no período da noite.",
                suggested_workflow={
                    "name": "Preparação para Estudo Noturno",
                    "trigger_config": {"type": "TIME", "time": "19:00", "days": ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]},
                    "safety_level": "AUTO_LOW_RISK",
                    "steps": [
                        {"name": "Iniciar Pomodoro de Foco", "action_type": "START_POMODORO", "parameters": {"duration_seconds": 1500}},
                        {"name": "Notificar Início", "action_type": "SHOW_NOTIFICATION", "parameters": {"title": "Hora de Estudar", "message": "Bloco de foco iniciado.", "type": "info"}}
                    ]
                },
                confidence=90,
                status="PENDING"
            )
            self.db.add(rec)
            recommendations.append(rec)

        await self.db.commit()
        for r in recommendations:
            await self.db.refresh(r)
            await event_bus.publish("WORKFLOW_RECOMMENDED", {
                "recommendation_id": r.recommendation_id,
                "title": r.title
            })

        return recommendations

    async def list_recommendations(self) -> List[WorkflowRecommendation]:
        stmt = select(WorkflowRecommendation).where(WorkflowRecommendation.status == "PENDING").order_by(desc(WorkflowRecommendation.created_at))
        res = await self.db.execute(stmt)
        return list(res.scalars().all())

    async def accept_recommendation(self, recommendation_id: str) -> WorkflowRecommendation:
        stmt = select(WorkflowRecommendation).where(WorkflowRecommendation.recommendation_id == recommendation_id)
        res = await self.db.execute(stmt)
        rec = res.scalar_one_or_none()
        if rec:
            rec.status = "ACCEPTED"
            await self.db.commit()
            await self.db.refresh(rec)
            await event_bus.publish("WORKFLOW_RECOMMENDATION_ACCEPTED", {"recommendation_id": recommendation_id})
        return rec

    async def dismiss_recommendation(self, recommendation_id: str) -> WorkflowRecommendation:
        stmt = select(WorkflowRecommendation).where(WorkflowRecommendation.recommendation_id == recommendation_id)
        res = await self.db.execute(stmt)
        rec = res.scalar_one_or_none()
        if rec:
            rec.status = "DISMISSED"
            await self.db.commit()
            await self.db.refresh(rec)
            await event_bus.publish("WORKFLOW_RECOMMENDATION_DISMISSED", {"recommendation_id": recommendation_id})
        return rec

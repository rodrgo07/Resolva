from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.orchestration import WorkflowEventRule
from app.automation.workflow_conditions import WorkflowConditionsEngine

class EventRulesEngine:
    """
    Motor de Regras de Eventos e Prevenção de Loops / Cooldown (Fase 34).
    """

    MAX_CHAIN_DEPTH = 5
    _EVENT_TRIGGER_HISTORY: Dict[str, List[datetime]] = {}

    def __init__(self, db: AsyncSession):
        self.db = db

    async def evaluate_event(
        self,
        event_type: str,
        event_payload: Dict[str, Any],
        current_chain_depth: int = 0
    ) -> List[Tuple[WorkflowEventRule, Dict[str, Any]]]:
        """
        Avalia se o evento disparado deve ativar workflows homologados.
        Aplica verificação de anti-loop e cooldown estrito.
        """
        if current_chain_depth > self.MAX_CHAIN_DEPTH:
            return [] # Bloqueio de chain depth excessivo

        stmt = select(WorkflowEventRule).where(
            WorkflowEventRule.event_type == event_type.upper(),
            WorkflowEventRule.enabled == True
        )
        res = await self.db.execute(stmt)
        rules = res.scalars().all()

        matched: List[Tuple[WorkflowEventRule, Dict[str, Any]]] = []
        now = datetime.utcnow()

        for rule in rules:
            # 1. Cooldown Check
            if rule.last_triggered_at:
                elapsed = (now - rule.last_triggered_at).total_seconds()
                if elapsed < rule.cooldown_seconds:
                    continue # Em cooldown

            # 2. Rate Limiting por regra (Anti-Loop)
            key = f"{rule.rule_id}_{rule.workflow_id}"
            history = self._EVENT_TRIGGER_HISTORY.setdefault(key, [])
            # Limpa registros mais velhos que 60 segundos
            self._EVENT_TRIGGER_HISTORY[key] = [t for t in history if (now - t).total_seconds() < 60]

            if len(self._EVENT_TRIGGER_HISTORY[key]) >= 5:
                continue # Limite de 5 disparos por minuto atingido (loop prevent)

            # 3. Avaliação de Condições
            if rule.conditions:
                cond_passed = WorkflowConditionsEngine.evaluate_condition(rule.conditions, event_payload)
                if not cond_passed:
                    continue

            # Registra timestamp
            self._EVENT_TRIGGER_HISTORY[key].append(now)
            rule.last_triggered_at = now
            matched.append((rule, event_payload))

        await self.db.commit()
        return matched

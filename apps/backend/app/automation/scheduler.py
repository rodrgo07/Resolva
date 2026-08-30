import asyncio
from typing import Dict, Any, List
from datetime import datetime, time
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.database import async_session_maker
from app.models.automation import Automation, AutomationTrigger
from app.automation.engine import AutomationEngine
from app.automation.kill_switch import is_kill_switch_active
from app.core.logging import logger

class AutomationScheduler:
    """
    Agendador persistente de rotinas em background.
    Avalia gatilhos de tempo (Schedule, Diário, Semanal) e inicialização (Startup).
    """
    def __init__(self):
        self._is_running = False
        self._task: asyncio.Task | None = None

    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._loop())
        logger.info("AutomationScheduler iniciado com sucesso no backend.")

    async def stop(self):
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("AutomationScheduler finalizado.")

    async def _loop(self):
        while self._is_running:
            try:
                if not is_kill_switch_active():
                    await self.check_and_run_due_automations()
            except Exception as e:
                logger.error(f"Erro no ciclo do AutomationScheduler: {e}")

            # Avalia a cada 30 segundos
            await asyncio.sleep(30)

    async def check_and_run_due_automations(self):
        now = datetime.now()
        current_time_str = now.strftime("%H:%M")
        current_weekday = now.weekday() # 0 = Monday, 6 = Sunday

        async with async_session_maker() as db:
            stmt = select(Automation).options(
                selectinload(Automation.triggers),
                selectinload(Automation.actions)
            ).where(Automation.is_active == True)
            res = await db.execute(stmt)
            automations = res.scalars().all()

            for auto in automations:
                for trig in auto.triggers:
                    trig_type = trig.type.upper()
                    config = trig.config or {}

                    # 1. Schedule Diário / Horário Fixo
                    if trig_type in ["SCHEDULE", "TIME", "DAILY"]:
                        target_time = config.get("time", "08:00")
                        days = config.get("days", []) # ex: [0, 1, 2, 3, 4]
                        
                        # Se dias foram especificados e hoje não coincide
                        if days and current_weekday not in days:
                            continue

                        # Se coincide o horário (minuto atual)
                        if target_time == current_time_str:
                            engine = AutomationEngine(db)
                            await engine.run_automation(auto.id, is_confirmed=True)

scheduler = AutomationScheduler()

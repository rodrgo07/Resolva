import asyncio
from typing import Optional
from datetime import datetime
from app.database import async_session_maker
from app.notifications.engine import NotificationEngine
from app.notifications.analyzers import (
    TaskNotificationAnalyzer,
    CalendarNotificationAnalyzer,
    EmailNotificationAnalyzer,
    StudyNotificationAnalyzer,
    FinanceNotificationAnalyzer
)
from app.notifications.proactive_agent import ProactiveAgent
from app.automation.kill_switch import is_kill_switch_active
from app.core.logging import logger

class NotificationScheduler:
    """
    Scheduler em background que avalia periodicamente o estado do sistema,
    dispara os analisadores e alimenta o NotificationEngine.
    """
    def __init__(self, interval_seconds: int = 30):
        self.interval_seconds = interval_seconds
        self._is_running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        if self._is_running:
            return
        self._is_running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"NotificationScheduler iniciado com ciclo de {self.interval_seconds}s.")

    async def stop(self):
        self._is_running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("NotificationScheduler finalizado.")

    async def _loop(self):
        while self._is_running:
            try:
                if not is_kill_switch_active():
                    await self.run_analysis_cycle()
            except Exception as e:
                logger.error(f"Erro no ciclo de análise do NotificationScheduler: {e}")

            await asyncio.sleep(self.interval_seconds)

    async def run_analysis_cycle(self):
        async with async_session_maker() as db:
            engine = NotificationEngine(db)

            # 1. Limpeza automática de notificações expiradas ou antigas (retenção)
            try:
                await engine.repo.clean_expired_and_old(retention_days=30)
            except Exception as e:
                logger.debug(f"Erro na limpeza de retenção: {e}")

            # 2. Execução dos Analyzers de Domínio
            analyzers = [
                TaskNotificationAnalyzer.analyze(db),
                CalendarNotificationAnalyzer.analyze(db),
                EmailNotificationAnalyzer.analyze(db),
                StudyNotificationAnalyzer.analyze(db),
                FinanceNotificationAnalyzer.analyze(db),
                ProactiveAgent(db).analyze_context_and_recommend()
            ]

            results = await asyncio.gather(*analyzers, return_exceptions=True)

            for batch in results:
                if isinstance(batch, list):
                    for notif_in in batch:
                        try:
                            await engine.create_notification(notif_in)
                        except Exception as notif_err:
                            logger.error(f"Erro ao processar notificação gerada: {notif_err}")

notification_scheduler = NotificationScheduler()

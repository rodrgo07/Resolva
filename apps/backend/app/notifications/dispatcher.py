from typing import Dict, Any, Optional
from datetime import datetime
from app.core.logging import logger

class NotificationDispatcher:
    """
    Dispatcher de notificações para In-App Center, Windows Toast e System Tray.
    """
    def __init__(self):
        pass

    async def dispatch_windows_toast(
        self,
        title: str,
        message: str,
        priority: str = "NORMAL",
        action_type: Optional[str] = None
    ) -> bool:
        """
        Emite notificação nativa para o Windows.
        No host desktop, o backend envia sinal ou loga; o front/Tauri recebe via push/polling.
        """
        logger.info(f"[Windows Toast Dispatched] [{priority}] {title} - {message}")
        return True

    async def dispatch_in_app(self, notification_dict: Dict[str, Any]) -> bool:
        """
        Notificação persistida no In-App Center.
        """
        logger.info(f"[In-App Notification Registered] {notification_dict.get('title')}")
        return True

dispatcher = NotificationDispatcher()

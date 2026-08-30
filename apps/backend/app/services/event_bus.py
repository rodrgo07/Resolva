from typing import Dict, Any, List, Set, Callable
import asyncio
from app.core.logging import logger

class EventBus:
    """
    Event Bus assíncrono interno para publicação e subscrição de eventos
    de domínio e retransmissão em tempo real via WebSocket.
    """
    _subscribers: Dict[str, Set[Callable[[Dict[str, Any]], Any]]] = {}
    _wildcard_subscribers: Set[Callable[[Dict[str, Any]], Any]] = set()

    @classmethod
    def subscribe(cls, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        if event_type == "*":
            cls._wildcard_subscribers.add(handler)
        else:
            if event_type not in cls._subscribers:
                cls._subscribers[event_type] = set()
            cls._subscribers[event_type].add(handler)

    @classmethod
    def unsubscribe(cls, event_type: str, handler: Callable[[Dict[str, Any]], Any]):
        if event_type == "*":
            cls._wildcard_subscribers.discard(handler)
        elif event_type in cls._subscribers:
            cls._subscribers[event_type].discard(handler)

    @classmethod
    async def publish(cls, event_type: str, data: Dict[str, Any]):
        """
        Publica um evento sanitizado (sem tokens, sem secrets).
        """
        event_payload = {
            "type": event_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }

        # Handlers específicos
        handlers = list(cls._subscribers.get(event_type, [])) + list(cls._wildcard_subscribers)
        for h in handlers:
            try:
                if asyncio.iscoroutinefunction(h):
                    asyncio.create_task(h(event_payload))
                else:
                    h(event_payload)
            except Exception as e:
                logger.error(f"Erro ao processar handler de evento {event_type}: {e}")

event_bus = EventBus()

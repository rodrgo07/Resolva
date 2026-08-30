from typing import Dict, Any, Set, List
from fastapi import WebSocket
import json
import asyncio
from app.services.event_bus import event_bus
from app.core.logging import logger

class RealtimeConnectionManager:
    """
    Gerencia conexões WebSocket autenticadas de dispositivos móveis e desktop,
    enviando heartbeats periódicos e transmitindo eventos em tempo real.
    """
    def __init__(self):
        # Mapeia device_id -> Set de WebSockets ativos
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Assina todos os eventos do event bus
        event_bus.subscribe("*", self.broadcast_event)

    async def connect(self, device_id: str, websocket: WebSocket):
        await websocket.accept()
        if device_id not in self.active_connections:
            self.active_connections[device_id] = set()
        self.active_connections[device_id].add(websocket)
        logger.info(f"WebSocket conectado para dispositivo {device_id}")

        # Notifica conexão
        await event_bus.publish("DEVICE_CONNECTED", {"device_id": device_id})

    def disconnect(self, device_id: str, websocket: WebSocket):
        if device_id in self.active_connections:
            self.active_connections[device_id].discard(websocket)
            if not self.active_connections[device_id]:
                del self.active_connections[device_id]
        logger.info(f"WebSocket desconectado para dispositivo {device_id}")

    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.warning(f"Erro ao enviar mensagem WebSocket individual: {e}")

    async def broadcast_to_device(self, device_id: str, message: Dict[str, Any]):
        if device_id in self.active_connections:
            text = json.dumps(message)
            dead_sockets = set()
            for ws in self.active_connections[device_id]:
                try:
                    await ws.send_text(text)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                self.active_connections[device_id].discard(dead)

    async def broadcast_event(self, event_payload: Dict[str, Any]):
        """
        Transmite o evento do EventBus para todos os clientes conectados.
        """
        text = json.dumps(event_payload)
        for device_id, sockets in list(self.active_connections.items()):
            dead_sockets = set()
            for ws in list(sockets):
                try:
                    await ws.send_text(text)
                except Exception:
                    dead_sockets.add(ws)
            for dead in dead_sockets:
                sockets.discard(dead)

realtime_manager = RealtimeConnectionManager()

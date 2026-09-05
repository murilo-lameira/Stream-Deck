import asyncio
import logging
from typing import List
from fastapi import WebSocket

logger = logging.getLogger("streamdeck.connection")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        self.active_connections.append(websocket)
        logger.info(f"Cliente WebSocket conectado. Conexoes ativas: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Cliente WebSocket desconectado. Conexoes ativas: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        if not self.active_connections:
            return

        dead_connections = []
        for connection in list(self.active_connections):
            try:
                await asyncio.wait_for(connection.send_json(message), timeout=1.0)
            except Exception as e:
                logger.debug(f"Falha ao enviar broadcast para conexao: {e}")
                dead_connections.append(connection)

        for dead in dead_connections:
            self.disconnect(dead)

manager = ConnectionManager()

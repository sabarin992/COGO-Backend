from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections = {}

    async def connect(
        self,
        conversation_id: int,
        websocket: WebSocket
    ):
        await websocket.accept()

        if conversation_id not in self.active_connections:
            self.active_connections[conversation_id] = []

        self.active_connections[conversation_id].append(websocket)

    def disconnect(
        self,
        conversation_id: int,
        websocket: WebSocket
    ):
        if conversation_id in self.active_connections:
            self.active_connections[conversation_id].remove(websocket)

            if not self.active_connections[conversation_id]:
                del self.active_connections[conversation_id]

    async def send_message(
        self,
        conversation_id: int,
        message: dict
    ):
        if conversation_id in self.active_connections:

            for connection in self.active_connections[conversation_id]:
                await connection.send_json(message)
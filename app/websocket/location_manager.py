from fastapi import WebSocket


class LocationManager:
    """
    Manages active WebSocket connections for live location tracking.

    Connections are grouped by ride_id (int). Any number of clients
    (driver + passengers) may share the same room. The driver broadcasts
    location updates; passenger connections passively receive them.

    This is intentionally kept separate from the chat ConnectionManager so
    that the two features remain independently maintainable.
    """

    def __init__(self):
        # { ride_id: [WebSocket, ...] }
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, ride_id: int, websocket: WebSocket) -> None:
        """Accept the WebSocket and register it under ride_id."""
        await websocket.accept()

        if ride_id not in self.active_connections:
            self.active_connections[ride_id] = []

        self.active_connections[ride_id].append(websocket)

    def disconnect(self, ride_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket from the room. Cleans up the room if empty."""
        if ride_id not in self.active_connections:
            return

        try:
            self.active_connections[ride_id].remove(websocket)
        except ValueError:
            # Already removed; nothing to do.
            pass

        if not self.active_connections[ride_id]:
            del self.active_connections[ride_id]

    async def broadcast(self, ride_id: int, message: dict) -> None:
        """
        Send a JSON message to every connection in the ride_id room.

        Connections that have already closed are silently removed so that a
        single stale socket does not block the entire broadcast.
        """
        if ride_id not in self.active_connections:
            return

        stale: list[WebSocket] = []

        for connection in list(self.active_connections[ride_id]):
            try:
                await connection.send_json(message)
            except Exception:
                # The client disconnected without a clean close frame.
                stale.append(connection)

        for connection in stale:
            self.disconnect(ride_id, connection)

import logging
from typing import Dict, List, Optional
from fastapi import WebSocket

logger = logging.getLogger("cogo.websocket.location")


class LocationManager:
    """
    Manages active WebSocket connections for live ride location tracking.

    Connections are grouped by ride_id (int). The driver sends GPS updates;
    accepted passengers passively receive them.
    Also caches the last known location for each active ride so that newly
    connected passengers receive an immediate location fix.
    """

    def __init__(self):
        # { ride_id: [WebSocket, ...] }
        self.active_connections: Dict[int, List[WebSocket]] = {}
        # { ride_id: { "type": "location", "ride_id": int, "lat": float, "lng": float, "timestamp": str } }
        self.last_known_locations: Dict[int, dict] = {}

    async def connect(self, ride_id: int, websocket: WebSocket) -> None:
        """Accept the WebSocket and register it under ride_id."""
        await websocket.accept()

        if ride_id not in self.active_connections:
            self.active_connections[ride_id] = []

        self.active_connections[ride_id].append(websocket)
        logger.info(
            "WebSocket connection accepted for ride_id=%d. Total connections in room: %d",
            ride_id,
            len(self.active_connections[ride_id]),
        )

    def disconnect(self, ride_id: int, websocket: WebSocket) -> None:
        """Remove a WebSocket from the ride room. Cleans up empty room."""
        if ride_id not in self.active_connections:
            return

        try:
            self.active_connections[ride_id].remove(websocket)
        except ValueError:
            pass

        if not self.active_connections[ride_id]:
            del self.active_connections[ride_id]
            logger.info("Room for ride_id=%d is now empty and has been removed.", ride_id)
        else:
            logger.info(
                "WebSocket disconnected from ride_id=%d. Remaining in room: %d",
                ride_id,
                len(self.active_connections[ride_id]),
            )

    async def broadcast(self, ride_id: int, message: dict) -> int:
        """
        Broadcast a location message to all active WebSockets for this ride.
        Returns the number of recipients successfully notified.
        """
        # Cache the latest valid location
        self.last_known_locations[ride_id] = message

        if ride_id not in self.active_connections:
            return 0

        stale: List[WebSocket] = []
        sent_count = 0

        for connection in list(self.active_connections[ride_id]):
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.warning("Failed to send message to connection in ride_id=%d: %s", ride_id, e)
                stale.append(connection)

        for connection in stale:
            self.disconnect(ride_id, connection)

        return sent_count

    def get_last_location(self, ride_id: int) -> Optional[dict]:
        """Return the most recent broadcast location for this ride, if any."""
        return self.last_known_locations.get(ride_id)

    def clear_ride(self, ride_id: int) -> None:
        """Clear cached location and active connections when ride ends."""
        self.last_known_locations.pop(ride_id, None)
        self.active_connections.pop(ride_id, None)


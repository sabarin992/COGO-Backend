from datetime import datetime, timezone
from json import JSONDecodeError

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user_ws
from app.models.ride import RideStatus
from app.repositories.ride_repo import (
    get_ride_by_id_only,
)
from app.repositories.ride_request_repo import get_request_by_ride_and_passenger
from app.websocket.location_manager import LocationManager

router = APIRouter()

# Module-level singleton — intentionally separate from the chat ConnectionManager.
location_manager = LocationManager()

# Ride statuses during which location sharing is permitted.
_ACTIVE_STATUSES = {
    RideStatus.STARTED,
    RideStatus.REACHED_PICKUP,
    RideStatus.ONGOING,
}

# RideRequest statuses that qualify a passenger to receive location updates.
# Values are the exact string literals written by ride_request_repo and ride_service.
_PASSENGER_ALLOWED_STATUSES = {"accepted", "picked_up"}


@router.websocket("/ws/{ride_id}")
async def location_websocket(
    ride_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_ws),
):
    """
    WebSocket endpoint for live driver location tracking.

    Full URL:  ws://<host>/api/v1/location/ws/{ride_id}
    Auth:      Cookie-based JWT — the same ``access_token`` httpOnly cookie
               used by all other WebSocket endpoints.

    ── Connection rules ─────────────────────────────────────────────────────
    • The ride must exist.
    • ``ride.status`` must be STARTED, REACHED_PICKUP, or ONGOING.
    • The connecting user must be either:
        – the driver  (``ride.driver_id == user.id``), OR
        – a passenger whose RideRequest for this ride has status
          ``"accepted"`` or ``"picked_up"``.
    • All other connections are rejected immediately with close code 1008.

    ── Driver behaviour (publish) ────────────────────────────────────────────
    The driver sends text frames containing JSON:
        { "lat": <float>, "lng": <float> }

    Before broadcasting, the server re-fetches the ride status from the DB.
    If the ride is no longer in an active status the update is rejected with:
        { "type": "error", "detail": "Ride is no longer active." }

    On a valid, in-range frame the server broadcasts to every connection in
    the room (driver included):
        {
            "type":      "location",
            "ride_id":   <int>,
            "lat":       <float>,
            "lng":       <float>,
            "timestamp": "<ISO-8601 UTC string>"
        }

    Validation errors produce a response sent only to the driver:
        { "type": "error", "detail": "<reason>" }

    Malformed JSON frames are caught and answered with the same error frame.
    They do NOT terminate the connection.

    ── Passenger behaviour (subscribe) ──────────────────────────────────────
    Passengers receive broadcast frames. Any data they send is silently
    discarded.

    ── Disconnection ─────────────────────────────────────────────────────────
    The connection is removed from LocationManager in a ``finally`` block so
    that cleanup always runs regardless of whether the disconnect was clean
    (WebSocketDisconnect), caused by a protocol error, or any other exception.
    """

    # ── 1. Fetch the ride ────────────────────────────────────────────────────
    ride = get_ride_by_id_only(db=db, ride_id=ride_id)

    if not ride:
        await websocket.close(code=1008, reason="Ride not found")
        return

    # ── 2. Gate on active tracking status ────────────────────────────────────
    if ride.status not in _ACTIVE_STATUSES:
        await websocket.close(
            code=1008,
            reason=(
                f"Location tracking is only available when the ride is in "
                f"STARTED, REACHED_PICKUP, or ONGOING status. "
                f"Current status: {ride.status}"
            ),
        )
        return

    # ── 3. Authorise the connecting user ─────────────────────────────────────
    # ride.driver_id is the Column name confirmed in app/models/ride.py
    is_driver = ride.driver_id == user.id

    if not is_driver:
        ride_request = get_request_by_ride_and_passenger(
            db=db,
            ride_id=ride_id,
            passenger_id=user.id,
        )

        is_authorised_passenger = (
            ride_request is not None
            and ride_request.status in _PASSENGER_ALLOWED_STATUSES
        )

        if not is_authorised_passenger:
            await websocket.close(
                code=1008,
                reason="Not authorised to track this ride",
            )
            return

    # ── 4. Join the room ─────────────────────────────────────────────────────
    # location_manager.connect() calls websocket.accept() internally.
    await location_manager.connect(ride_id, websocket)

    try:
        while True:
            # ── 4a. Receive next frame ───────────────────────────────────────
            # receive_json() raises:
            #   WebSocketDisconnect  – clean or unclean client disconnect
            #   JSONDecodeError      – client sent a non-JSON text frame
            try:
                data = await websocket.receive_json()
            except JSONDecodeError:
                # Malformed JSON from driver: send error and keep connection open.
                # Malformed JSON from passenger: silently discard (they send nothing).
                if is_driver:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "detail": "Invalid JSON — expected {\"lat\": <float>, \"lng\": <float>}",
                        }
                    )
                continue

            # Passengers are subscribe-only; discard anything they send.
            if not is_driver:
                continue

            # ── 4b. Re-validate ride is still active (per-update check) ─────
            # Refresh ride status from DB so that a completed/cancelled ride
            # cannot keep receiving driver updates after the transition.
            current_ride = get_ride_by_id_only(db=db, ride_id=ride_id)
            if current_ride is None or current_ride.status not in _ACTIVE_STATUSES:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Ride is no longer active. Please close the connection.",
                    }
                )
                continue

            # ── 4c. Validate coordinate values ──────────────────────────────
            lat = data.get("lat")
            lng = data.get("lng")

            if lat is None or lng is None:
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "Missing required fields: lat, lng",
                    }
                )
                continue

            try:
                lat = float(lat)
                lng = float(lng)
            except (TypeError, ValueError):
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "lat and lng must be numeric",
                    }
                )
                continue

            if not (-90.0 <= lat <= 90.0):
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "lat must be between -90 and 90",
                    }
                )
                continue

            if not (-180.0 <= lng <= 180.0):
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "lng must be between -180 and 180",
                    }
                )
                continue

            # ── 4d. Broadcast to all room members ────────────────────────────
            # broadcast() iterates a copy of the connection list and silently
            # removes any socket that fails to send (stale connections).
            await location_manager.broadcast(
                ride_id=ride_id,
                message={
                    "type": "location",
                    "ride_id": ride_id,
                    "lat": lat,
                    "lng": lng,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                },
            )

    except WebSocketDisconnect:
        # Clean or unclean client disconnect — handled by finally below.
        pass

    finally:
        # Always remove from the room, regardless of how the loop exited.
        # LocationManager.disconnect() is idempotent if already removed.
        location_manager.disconnect(ride_id, websocket)

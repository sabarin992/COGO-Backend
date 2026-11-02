import logging
from datetime import datetime, timezone
from json import JSONDecodeError
from typing import Any

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user_ws
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest
from app.repositories.ride_repo import get_ride_by_id_only
from app.websocket.location_manager import LocationManager

logger = logging.getLogger("cogo.location")
router = APIRouter()

# Singleton LocationManager
location_manager = LocationManager()

_ACTIVE_STATUS_VALUES = {
    RideStatus.STARTED.value,
    RideStatus.REACHED_PICKUP.value,
    RideStatus.ONGOING.value,
}

_PASSENGER_ALLOWED_STATUSES = {"accepted", "picked_up"}


def _get_status_str(status: Any) -> str:
    """Helper to get string value from string or RideStatus enum."""
    if hasattr(status, "value"):
        return str(status.value)
    return str(status)


@router.websocket("/ws/{ride_id}")
async def location_websocket(
    ride_id: int,
    websocket: WebSocket,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_ws),
):
    """
    WebSocket endpoint for live driver location tracking and broadcasting.

    Endpoint URL: ws://<host>/api/v1/location/ws/{ride_id}
    Authentication: HttpOnly access_token cookie validated via get_current_user_ws.
    """
    client_host = websocket.client.host if websocket.client else "unknown"
    logger.info(
        "WebSocket connection attempt: ride_id=%d, user_id=%d, client_ip=%s",
        ride_id,
        user.id,
        client_host,
    )

    # 1. Verify ride exists
    ride = get_ride_by_id_only(db=db, ride_id=ride_id)
    if not ride:
        logger.warning(
            "WebSocket rejected: ride_id=%d not found. user_id=%d",
            ride_id,
            user.id,
        )
        await websocket.close(code=1008, reason="Ride not found")
        return

    # 2. Verify ride is in an active tracking status
    ride_status_str = _get_status_str(ride.status)
    if ride_status_str not in _ACTIVE_STATUS_VALUES:
        logger.warning(
            "WebSocket rejected: ride_id=%d is in inactive status '%s'. user_id=%d",
            ride_id,
            ride_status_str,
            user.id,
        )
        await websocket.close(
            code=1008,
            reason=(
                f"Location tracking is only available when the ride is in "
                f"STARTED, REACHED_PICKUP, or ONGOING status. "
                f"Current status: {ride_status_str}"
            ),
        )
        return

    # 3. Authorize the user (Driver or Accepted/Picked-up Passenger)
    is_driver = ride.driver_id == user.id

    if not is_driver:
        # Check if user has an accepted or picked_up booking for this ride
        ride_request = (
            db.query(RideRequest)
            .filter(
                RideRequest.ride_id == ride_id,
                RideRequest.passenger_id == user.id,
                RideRequest.status.in_(_PASSENGER_ALLOWED_STATUSES),
            )
            .first()
        )

        if not ride_request:
            logger.warning(
                "WebSocket authorization failed: user_id=%d is neither driver nor accepted passenger for ride_id=%d",
                user.id,
                ride_id,
            )
            await websocket.close(
                code=1008,
                reason="Not authorised to track this ride",
            )
            return

        role = "passenger"
        logger.info(
            "Passenger connection authorized: user_id=%d, booking_id=%d, ride_id=%d",
            user.id,
            ride_request.ride_request_id,
            ride_id,
        )
    else:
        role = "driver"
        logger.info(
            "Driver connection authorized: user_id=%d, ride_id=%d",
            user.id,
            ride_id,
        )

    # 4. Connect to LocationManager room
    await location_manager.connect(ride_id, websocket)

    # If passenger joins and a cached location exists, immediately send it
    if not is_driver:
        last_loc = location_manager.get_last_location(ride_id)
        if last_loc:
            try:
                await websocket.send_json(last_loc)
                logger.info(
                    "Sent cached location to passenger user_id=%d for ride_id=%d",
                    user.id,
                    ride_id,
                )
            except Exception as e:
                logger.warning(
                    "Failed to send cached location to passenger user_id=%d: %s",
                    user.id,
                    e,
                )

    # 5. Main loop
    try:
        while True:
            try:
                data = await websocket.receive_json()
            except JSONDecodeError:
                if is_driver:
                    await websocket.send_json(
                        {
                            "type": "error",
                            "detail": 'Invalid JSON — expected {"lat": <float>, "lng": <float>}',
                        }
                    )
                continue

            # Passengers are receive-only subscribers; discard any incoming frames
            if not is_driver:
                continue

            # Validate payload is a dictionary
            if not isinstance(data, dict):
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": 'Expected a JSON object: {"lat": <float>, "lng": <float>}',
                    }
                )
                continue

            # Re-check that the ride is still active
            current_ride = get_ride_by_id_only(db=db, ride_id=ride_id)
            if not current_ride or _get_status_str(current_ride.status) not in _ACTIVE_STATUS_VALUES:
                logger.info(
                    "Closing location WebSocket: ride_id=%d is no longer active (status=%s)",
                    ride_id,
                    _get_status_str(current_ride.status) if current_ride else "None",
                )
                await websocket.close(
                    code=1008,
                    reason="Ride is no longer active",
                )
                break

            # Validate lat/lng
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

            if isinstance(lat, bool) or isinstance(lng, bool):
                await websocket.send_json(
                    {
                        "type": "error",
                        "detail": "lat and lng must be numbers, not booleans",
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

            # Broadcast location update to all connections in room
            location_msg = {
                "type": "location",
                "ride_id": ride_id,
                "lat": lat,
                "lng": lng,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            recipients = await location_manager.broadcast(ride_id, location_msg)
            logger.debug(
                "Broadcast location for ride_id=%d to %d recipients (lat=%.5f, lng=%.5f)",
                ride_id,
                recipients,
                lat,
                lng,
            )

    except WebSocketDisconnect as e:
        logger.info(
            "WebSocket disconnected: ride_id=%d, user_id=%d, role=%s, code=%s",
            ride_id,
            user.id,
            role,
            e.code if hasattr(e, "code") else "normal",
        )
    except Exception as e:
        logger.error(
            "Unexpected error in location WebSocket: ride_id=%d, user_id=%d, role=%s: %s",
            ride_id,
            user.id,
            role,
            e,
        )
    finally:
        location_manager.disconnect(ride_id, websocket)
        logger.info(
            "WebSocket connection cleaned up: ride_id=%d, user_id=%d, role=%s",
            ride_id,
            user.id,
            role,
        )


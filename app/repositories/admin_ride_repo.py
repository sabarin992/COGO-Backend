from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import func, or_

from app.models.ride import Ride, RideStatus
from app.models.user import User
from app.models.vehicle import Vehicle
from app.models.ride_request import RideRequest


def get_admin_rides(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    query = db.query(Ride).join(User, Ride.driver_id == User.id)

    if search:
        search_clean = search.strip()
        conditions = [
            User.full_name.ilike(f"%{search_clean}%"),
            User.email.ilike(f"%{search_clean}%"),
            Ride.source.ilike(f"%{search_clean}%"),
            Ride.destination.ilike(f"%{search_clean}%"),
        ]

        # Check if search is a numeric ride ID or starts with "RD-"
        numeric_id = None
        if search_clean.isdigit():
            numeric_id = int(search_clean)
        elif search_clean.upper().startswith("RD-") and search_clean[3:].isdigit():
            numeric_id = int(search_clean[3:])

        if numeric_id is not None:
            conditions.append(Ride.ride_id == numeric_id)

        query = query.filter(or_(*conditions))

    if status and status.lower() != "all":
        # Match normalized upper case enum value
        query = query.filter(Ride.status == status.upper())

    total = query.count()
    offset = max(0, (page - 1) * size)
    rides = (
        query.options(joinedload(Ride.driver))
        .order_by(Ride.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    items = []
    for ride in rides:
        driver = ride.driver
        items.append({
            "ride_id": ride.ride_id,
            "driver_id": ride.driver_id,
            "driver_name": driver.full_name if driver else "Unknown",
            "driver_email": driver.email if driver else None,
            "driver_profile_pic": driver.profile_pic if driver else None,
            "source": ride.source,
            "destination": ride.destination,
            "travel_date": ride.travel_date,
            "travel_time": ride.travel_time,
            "available_seats": ride.available_seats,
            "status": ride.status,
            "created_at": ride.created_at,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 1,
    }


def get_admin_ride_stats(db: Session) -> Dict[str, int]:
    counts_by_status = dict(
        db.query(Ride.status, func.count(Ride.ride_id))
        .group_by(Ride.status)
        .all()
    )

    total = db.query(func.count(Ride.ride_id)).scalar() or 0

    return {
        "total": total,
        "created": counts_by_status.get(RideStatus.CREATED.value, 0),
        "upcoming": counts_by_status.get(RideStatus.UPCOMING.value, 0),
        "started": counts_by_status.get(RideStatus.STARTED.value, 0),
        "reached_pickup": counts_by_status.get(RideStatus.REACHED_PICKUP.value, 0),
        "ongoing": counts_by_status.get(RideStatus.ONGOING.value, 0),
        "completed": counts_by_status.get(RideStatus.COMPLETED.value, 0),
        "cancelled": counts_by_status.get(RideStatus.CANCELLED.value, 0),
    }


def get_admin_ride_by_id(db: Session, ride_id: int) -> Optional[Ride]:
    return (
        db.query(Ride)
        .options(
            joinedload(Ride.driver),
            joinedload(Ride.vehicle),
            joinedload(Ride.cancelled_by),
            selectinload(Ride.ride_requests).joinedload(RideRequest.passenger),
        )
        .filter(Ride.ride_id == ride_id)
        .first()
    )


def admin_cancel_ride(
    db: Session,
    ride_id: int,
    admin_id: int,
    reason: str,
) -> Optional[Ride]:
    ride = (
        db.query(Ride)
        .filter(Ride.ride_id == ride_id)
        .with_for_update()
        .first()
    )

    if not ride:
        return None

    # Update ride
    ride.status = RideStatus.CANCELLED.value
    ride.cancellation_reason = reason
    ride.cancelled_by_id = admin_id
    ride.cancelled_at = datetime.now(timezone.utc)

    # Cancel associated active ride requests
    requests = (
        db.query(RideRequest)
        .filter(
            RideRequest.ride_id == ride_id,
            RideRequest.status.in_(["pending", "accepted", "picked_up"]),
        )
        .all()
    )

    for req in requests:
        req.status = "cancelled"

    db.commit()
    db.refresh(ride)
    return ride


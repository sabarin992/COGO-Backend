from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import func, or_

from app.models.ride_request import RideRequest
from app.models.ride import Ride, RideStatus
from app.models.user import User
from app.models.vehicle import Vehicle


def get_admin_bookings(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    Passenger = aliased(User, name="passenger_user")
    Driver = aliased(User, name="driver_user")

    query = (
        db.query(RideRequest)
        .join(Passenger, RideRequest.passenger_id == Passenger.id)
        .join(Ride, RideRequest.ride_id == Ride.ride_id)
        .join(Driver, Ride.driver_id == Driver.id)
    )

    if search:
        search_clean = search.strip()
        conditions = [
            Passenger.full_name.ilike(f"%{search_clean}%"),
            Passenger.email.ilike(f"%{search_clean}%"),
            Driver.full_name.ilike(f"%{search_clean}%"),
            Driver.email.ilike(f"%{search_clean}%"),
            Ride.source.ilike(f"%{search_clean}%"),
            Ride.destination.ilike(f"%{search_clean}%"),
        ]

        numeric_id = None
        if search_clean.isdigit():
            numeric_id = int(search_clean)
        elif search_clean.upper().startswith("BK-") and search_clean[3:].isdigit():
            numeric_id = int(search_clean[3:])
        elif search_clean.upper().startswith("RD-") and search_clean[3:].isdigit():
            conditions.append(Ride.ride_id == int(search_clean[3:]))

        if numeric_id is not None:
            conditions.append(RideRequest.ride_request_id == numeric_id)
            conditions.append(Ride.ride_id == numeric_id)

        query = query.filter(or_(*conditions))

    if status and status.lower() != "all":
        norm_status = status.lower()
        if norm_status == "accepted":
            query = query.filter(RideRequest.status.in_(["accepted", "picked_up"]))
        else:
            query = query.filter(RideRequest.status == norm_status)

    total = query.count()
    offset = max(0, (page - 1) * size)
    bookings = (
        query.options(
            joinedload(RideRequest.passenger),
            joinedload(RideRequest.ride).joinedload(Ride.driver),
        )
        .order_by(RideRequest.created_at.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    items = []
    for b in bookings:
        p = b.passenger
        r = b.ride
        d = r.driver if r else None

        items.append({
            "booking_id": b.ride_request_id,
            "ride_id": b.ride_id,
            "passenger_id": b.passenger_id,
            "passenger_name": p.full_name if p else "Unknown",
            "passenger_email": p.email if p else None,
            "passenger_profile_pic": p.profile_pic if p else None,
            "driver_id": d.id if d else 0,
            "driver_name": d.full_name if d else "Unknown",
            "driver_email": d.email if d else None,
            "driver_profile_pic": d.profile_pic if d else None,
            "source": r.source if r else "N/A",
            "destination": r.destination if r else "N/A",
            "travel_date": r.travel_date if r else None,
            "travel_time": r.travel_time if r else None,
            "seats_requested": b.seats_requested,
            "status": b.status,
            "created_at": b.created_at,
        })

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 1,
    }


def get_admin_booking_stats(db: Session) -> Dict[str, int]:
    total = db.query(func.count(RideRequest.ride_request_id)).scalar() or 0
    counts = dict(
        db.query(RideRequest.status, func.count(RideRequest.ride_request_id))
        .group_by(RideRequest.status)
        .all()
    )

    pending = counts.get("pending", 0)
    accepted = counts.get("accepted", 0) + counts.get("picked_up", 0)
    rejected = counts.get("rejected", 0)
    cancelled = counts.get("cancelled", 0)

    return {
        "total": total,
        "pending": pending,
        "accepted": accepted,
        "rejected": rejected,
        "cancelled": cancelled,
    }


def get_admin_booking_by_id(db: Session, booking_id: int) -> Optional[RideRequest]:
    return (
        db.query(RideRequest)
        .options(
            joinedload(RideRequest.passenger),
            joinedload(RideRequest.cancelled_by),
            joinedload(RideRequest.ride).joinedload(Ride.driver),
            joinedload(RideRequest.ride).joinedload(Ride.vehicle),
        )
        .filter(RideRequest.ride_request_id == booking_id)
        .first()
    )


def admin_cancel_booking(
    db: Session,
    booking_id: int,
    admin_id: int,
    reason: str,
) -> Optional[RideRequest]:
    booking = (
        db.query(RideRequest)
        .options(
            joinedload(RideRequest.ride),
            joinedload(RideRequest.passenger),
        )
        .filter(RideRequest.ride_request_id == booking_id)
        .with_for_update()
        .first()
    )

    if not booking:
        return None

    # If the booking was accepted or picked_up, restore seats to the ride
    if booking.status in ["accepted", "picked_up"] and booking.ride:
        booking.ride.available_seats += booking.seats_requested

    booking.status = "cancelled"
    booking.cancellation_reason = reason
    booking.cancelled_by_id = admin_id
    booking.cancelled_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(booking)
    return booking


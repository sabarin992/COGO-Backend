from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.repositories import admin_booking_repo
from app.models.ride import RideStatus
from app.core.exceptions import NotFoundException, BadRequestException


def get_admin_bookings_service(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    return admin_booking_repo.get_admin_bookings(
        db=db,
        search=search,
        status=status,
        page=page,
        size=size,
    )


def get_admin_booking_stats_service(db: Session) -> Dict[str, int]:
    return admin_booking_repo.get_admin_booking_stats(db=db)


def get_admin_booking_details_service(db: Session, booking_id: int) -> Dict[str, Any]:
    booking = admin_booking_repo.get_admin_booking_by_id(db=db, booking_id=booking_id)

    if not booking:
        raise NotFoundException("Booking request not found.")

    p = booking.passenger
    r = booking.ride
    d = r.driver if r else None
    v = r.vehicle if r else None
    cancelled_by = booking.cancelled_by

    return {
        "booking_id": booking.ride_request_id,
        "status": booking.status,
        "seats_requested": booking.seats_requested,
        "cancellation_reason": booking.cancellation_reason,
        "cancelled_by_admin": cancelled_by.full_name if cancelled_by else None,
        "cancelled_at": booking.cancelled_at,
        "created_at": booking.created_at,
        "updated_at": booking.updated_at,
        "passenger": {
            "id": p.id if p else booking.passenger_id,
            "full_name": p.full_name if p else "Unknown",
            "email": p.email if p else None,
            "phone": p.phone if p else None,
            "profile_pic": p.profile_pic if p else None,
        },
        "driver": {
            "id": d.id if d else (r.driver_id if r else 0),
            "full_name": d.full_name if d else "Unknown",
            "email": d.email if d else None,
            "phone": d.phone if d else None,
            "profile_pic": d.profile_pic if d else None,
        },
        "ride": {
            "ride_id": r.ride_id if r else booking.ride_id,
            "source": r.source if r else "N/A",
            "destination": r.destination if r else "N/A",
            "travel_date": r.travel_date if r else None,
            "travel_time": r.travel_time if r else None,
            "available_seats": r.available_seats if r else 0,
            "status": r.status if r else "UNKNOWN",
        },
        "vehicle": {
            "id": v.id if v else (r.vehicle_id if r else 0),
            "vehicle_type": v.vehicle_type if v else "Unknown",
            "brand": v.brand if v else "",
            "model": v.model if v else "",
            "year": v.year if v else None,
            "color": v.color if v else None,
            "registration_number": v.registration_number if v else "N/A",
        } if v else None,
    }


def admin_cancel_booking_service(
    db: Session,
    booking_id: int,
    admin_id: int,
    reason: str,
) -> Dict[str, Any]:
    if not reason or not reason.strip():
        raise BadRequestException("A cancellation reason is mandatory.")

    booking = admin_booking_repo.get_admin_booking_by_id(db=db, booking_id=booking_id)
    if not booking:
        raise NotFoundException("Booking request not found.")

    if booking.status in ["rejected", "cancelled"]:
        raise BadRequestException(f"This booking request is already {booking.status}.")

    if booking.ride and booking.ride.status == RideStatus.COMPLETED.value:
        raise BadRequestException("Cannot cancel a booking associated with a completed ride.")

    cancelled = admin_booking_repo.admin_cancel_booking(
        db=db,
        booking_id=booking_id,
        admin_id=admin_id,
        reason=reason.strip(),
    )

    if not cancelled:
        raise NotFoundException("Failed to cancel booking.")

    return get_admin_booking_details_service(db=db, booking_id=booking_id)


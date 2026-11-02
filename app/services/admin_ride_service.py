from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.repositories import admin_ride_repo
from app.models.ride import RideStatus
from app.core.exceptions import NotFoundException, BadRequestException


def get_admin_rides_service(
    db: Session,
    search: Optional[str] = None,
    status: Optional[str] = None,
    page: int = 1,
    size: int = 10,
) -> Dict[str, Any]:
    return admin_ride_repo.get_admin_rides(
        db=db,
        search=search,
        status=status,
        page=page,
        size=size,
    )


def get_admin_ride_stats_service(db: Session) -> Dict[str, int]:
    return admin_ride_repo.get_admin_ride_stats(db=db)


def get_admin_ride_details_service(db: Session, ride_id: int) -> Dict[str, Any]:
    ride = admin_ride_repo.get_admin_ride_by_id(db=db, ride_id=ride_id)

    if not ride:
        raise NotFoundException("Ride not found.")

    driver = ride.driver
    vehicle = ride.vehicle
    cancelled_by = ride.cancelled_by

    passengers = []
    all_requests = []

    for req in ride.ride_requests:
        p = req.passenger
        req_item = {
            "ride_request_id": req.ride_request_id,
            "passenger_id": req.passenger_id,
            "full_name": p.full_name if p else "Unknown",
            "email": p.email if p else None,
            "phone": p.phone if p else None,
            "profile_pic": p.profile_pic if p else None,
            "seats_requested": req.seats_requested,
            "status": req.status,
            "created_at": req.created_at,
        }
        all_requests.append(req_item)

        if req.status in ["accepted", "picked_up"]:
            passengers.append(req_item)

    return {
        "ride_id": ride.ride_id,
        "source": ride.source,
        "destination": ride.destination,
        "route": ride.route,
        "route_geometry": ride.route_geometry,
        "travel_date": ride.travel_date,
        "travel_time": ride.travel_time,
        "available_seats": ride.available_seats,
        "status": ride.status,
        "cancellation_reason": ride.cancellation_reason,
        "cancelled_by_admin": cancelled_by.full_name if cancelled_by else None,
        "cancelled_at": ride.cancelled_at,
        "created_at": ride.created_at,
        "updated_at": ride.updated_at,
        "driver": {
            "id": driver.id if driver else ride.driver_id,
            "full_name": driver.full_name if driver else "Unknown",
            "email": driver.email if driver else None,
            "phone": driver.phone if driver else None,
            "profile_pic": driver.profile_pic if driver else None,
        },
        "vehicle": {
            "id": vehicle.id if vehicle else ride.vehicle_id,
            "vehicle_type": vehicle.vehicle_type if vehicle else "Unknown",
            "brand": vehicle.brand if vehicle else "",
            "model": vehicle.model if vehicle else "",
            "year": vehicle.year if vehicle else 0,
            "color": vehicle.color if vehicle else "",
            "registration_number": vehicle.registration_number if vehicle else "",
            "seating_capacity": vehicle.seating_capacity if vehicle else 0,
            "images": vehicle.images if vehicle else None,
        },
        "passengers": passengers,
        "requests": all_requests,
    }


def admin_cancel_ride_service(
    db: Session,
    ride_id: int,
    admin_id: int,
    reason: str,
) -> Dict[str, Any]:
    if not reason or not reason.strip():
        raise BadRequestException("A cancellation reason is mandatory.")

    # Check ride status first
    ride = admin_ride_repo.get_admin_ride_by_id(db=db, ride_id=ride_id)
    if not ride:
        raise NotFoundException("Ride not found.")

    if ride.status == RideStatus.COMPLETED.value:
        raise BadRequestException("Completed rides cannot be cancelled.")

    if ride.status == RideStatus.CANCELLED.value:
        raise BadRequestException("This ride has already been cancelled.")

    cancelled_ride = admin_ride_repo.admin_cancel_ride(
        db=db,
        ride_id=ride_id,
        admin_id=admin_id,
        reason=reason.strip(),
    )

    if not cancelled_ride:
        raise NotFoundException("Failed to cancel ride.")

    return get_admin_ride_details_service(db=db, ride_id=ride_id)


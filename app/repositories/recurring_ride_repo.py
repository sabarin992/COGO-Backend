from datetime import date
from typing import List, Optional, Set
from sqlalchemy.orm import Session, joinedload
from app.models.recurring_ride import RecurringRide
from app.models.ride import Ride, RideStatus
from app.models.ride_request import RideRequest
from app.schemas.recurring_ride import RecurringRideCreate


def create_recurring_ride(
    db: Session,
    data: RecurringRideCreate,
    driver_id: int,
) -> RecurringRide:
    recurring_ride = RecurringRide(
        driver_id=driver_id,
        vehicle_id=data.vehicle_id,
        source=data.source,
        destination=data.destination,
        route=data.route,
        route_geometry=data.route_geometry,
        available_seats=data.available_seats,
        travel_time=data.travel_time,
        recurrence_type=data.recurrence_type.value,
        start_date=data.start_date,
        end_date=data.end_date,
        selected_weekdays=data.selected_weekdays,
        working_days=data.working_days,
        off_days=data.off_days,
        shift_start_date=data.shift_start_date,
        is_active=True,
    )
    db.add(recurring_ride)
    db.flush()
    return recurring_ride


def get_recurring_ride_by_id(
    db: Session,
    recurring_ride_id: int,
    driver_id: Optional[int] = None,
) -> Optional[RecurringRide]:
    query = (
        db.query(RecurringRide)
        .options(
            joinedload(RecurringRide.vehicle),
            joinedload(RecurringRide.rides).joinedload(Ride.ride_requests),
        )
        .filter(RecurringRide.id == recurring_ride_id)
    )
    if driver_id is not None:
        query = query.filter(RecurringRide.driver_id == driver_id)
    return query.first()


def get_driver_recurring_rides(
    db: Session,
    driver_id: int,
) -> List[RecurringRide]:
    return (
        db.query(RecurringRide)
        .options(
            joinedload(RecurringRide.vehicle),
            joinedload(RecurringRide.rides).joinedload(Ride.ride_requests),
        )
        .filter(RecurringRide.driver_id == driver_id)
        .order_by(RecurringRide.created_at.desc())
        .all()
    )


def get_all_active_recurring_rides(db: Session) -> List[RecurringRide]:
    return (
        db.query(RecurringRide)
        .filter(
            RecurringRide.is_active.is_(True),
            RecurringRide.end_date >= date.today(),
        )
        .all()
    )


def get_schedule_existing_dates(db: Session, recurring_ride_id: int) -> Set[date]:
    results = (
        db.query(Ride.travel_date)
        .filter(Ride.recurring_ride_id == recurring_ride_id)
        .all()
    )
    return {r[0] for r in results}


def get_future_unbooked_rides(
    db: Session,
    recurring_ride_id: int,
    from_date: date,
) -> List[Ride]:
    """
    Returns future rides belonging to this schedule that have NO passenger bookings.
    A ride is considered booked if it has any ride request with accepted or picked_up status.
    """
    all_future_rides = (
        db.query(Ride)
        .options(joinedload(Ride.ride_requests))
        .filter(
            Ride.recurring_ride_id == recurring_ride_id,
            Ride.travel_date >= from_date,
            Ride.status.in_([RideStatus.CREATED, RideStatus.UPCOMING]),
        )
        .all()
    )

    unbooked_rides: List[Ride] = []
    for r in all_future_rides:
        has_bookings = any(
            req.status in ["accepted", "picked_up", "pending"]
            for req in (r.ride_requests or [])
        )
        if not has_bookings:
            unbooked_rides.append(r)

    return unbooked_rides


def update_recurring_ride(
    db: Session,
    recurring_ride: RecurringRide,
    update_data: dict,
) -> RecurringRide:
    for key, value in update_data.items():
        if hasattr(recurring_ride, key) and value is not None:
            setattr(recurring_ride, key, value)
    db.flush()
    return recurring_ride


def delete_recurring_ride(
    db: Session,
    recurring_ride: RecurringRide,
) -> None:
    db.delete(recurring_ride)
    db.flush()

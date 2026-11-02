from datetime import date, datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.ride import Ride, RideStatus
from app.models.recurring_ride import RecurringRide
from app.schemas.recurring_ride import (
    RecurringRideCreate,
    RecurringRideUpdate,
    RecurringRideResponse,
    RecurringRideDetailsResponse,
    GeneratedRideItem,
)
from app.repositories import (
    recurring_ride_repo,
    vehicle_repo,
    user_repo,
)
from app.services.recurrence_utils import calculate_recurrence_dates
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)


def _compute_schedule_status(recurring: RecurringRide) -> str:
    if not recurring.is_active:
        return "Paused"
    if recurring.end_date < date.today():
        return "Completed"
    return "Active"


def generate_rides_for_schedule(
    db: Session,
    recurring: RecurringRide,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
) -> int:
    """
    Idempotently generates Ride rows for the given schedule.
    Returns the number of newly created rides.
    """
    min_date = date.today()
    start = max(recurring.start_date, from_date or recurring.start_date, min_date)
    end = min(recurring.end_date, to_date or recurring.end_date)

    if start > end:
        return 0

    target_dates = calculate_recurrence_dates(
        recurrence_type=recurring.recurrence_type,
        start_date=start,
        end_date=end,
        selected_weekdays=recurring.selected_weekdays,
        working_days=recurring.working_days,
        off_days=recurring.off_days,
        shift_start_date=recurring.shift_start_date,
        min_date=min_date,
    )

    existing_dates = recurring_ride_repo.get_schedule_existing_dates(db, recurring.id)
    new_rides = []

    for d in target_dates:
        if d not in existing_dates:
            ride = Ride(
                driver_id=recurring.driver_id,
                vehicle_id=recurring.vehicle_id,
                recurring_ride_id=recurring.id,
                source=recurring.source,
                destination=recurring.destination,
                route=recurring.route,
                route_geometry=recurring.route_geometry,
                travel_date=d,
                travel_time=recurring.travel_time,
                available_seats=recurring.available_seats,
                status=RideStatus.CREATED.value,
            )
            db.add(ride)
            new_rides.append(ride)

    db.flush()
    return len(new_rides)


def create_recurring_ride(
    db: Session,
    ride_data: RecurringRideCreate,
    email: str,
) -> RecurringRideDetailsResponse:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    if user.role != "rider":
        raise ForbiddenException("Only users with the Rider role can post a ride.")

    vehicle = vehicle_repo.get_vehicle_by_id(db, ride_data.vehicle_id)
    if not vehicle:
        raise NotFoundException("Vehicle not found.")

    if vehicle.user_id != user.id:
        raise ForbiddenException("You can only post rides using your own vehicle.")

    if ride_data.available_seats > vehicle.seating_capacity:
        raise BadRequestException(
            f"Available seats cannot exceed the vehicle seating capacity ({vehicle.seating_capacity})."
        )

    # Pre-calculate to ensure at least one future date will be generated
    projected_dates = calculate_recurrence_dates(
        recurrence_type=ride_data.recurrence_type,
        start_date=ride_data.start_date,
        end_date=ride_data.end_date,
        selected_weekdays=ride_data.selected_weekdays,
        working_days=ride_data.working_days,
        off_days=ride_data.off_days,
        shift_start_date=ride_data.shift_start_date,
        min_date=date.today(),
    )

    if not projected_dates:
        raise BadRequestException(
            "No valid upcoming journey dates found for the selected recurrence schedule."
        )

    # 1. Create schedule
    recurring = recurring_ride_repo.create_recurring_ride(
        db=db,
        data=ride_data,
        driver_id=user.id,
    )

    # 2. Generate initial rides
    generate_rides_for_schedule(db, recurring)

    db.commit()
    db.refresh(recurring)

    return get_recurring_ride_details_service(db, recurring.id, email)


def get_driver_recurring_rides_service(
    db: Session,
    email: str,
) -> List[RecurringRideResponse]:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    schedules = recurring_ride_repo.get_driver_recurring_rides(db, user.id)
    today = date.today()
    results = []

    for s in schedules:
        total = len(s.rides)
        upcoming = sum(1 for r in s.rides if r.travel_date >= today and r.status != RideStatus.CANCELLED.value)
        booked = sum(
            1 for r in s.rides
            if any(req.status in ["accepted", "picked_up", "pending"] for req in (r.ride_requests or []))
        )

        resp = RecurringRideResponse.model_validate(s)
        resp.total_rides = total
        resp.upcoming_rides = upcoming
        resp.booked_rides_count = booked
        resp.schedule_status = _compute_schedule_status(s)
        results.append(resp)

    return results


def get_recurring_ride_details_service(
    db: Session,
    recurring_ride_id: int,
    email: str,
) -> RecurringRideDetailsResponse:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    recurring = recurring_ride_repo.get_recurring_ride_by_id(db, recurring_ride_id, user.id)
    if not recurring:
        raise NotFoundException("Recurring ride schedule not found.")

    today = date.today()
    rides_list = sorted(recurring.rides, key=lambda r: r.travel_date)
    total = len(rides_list)
    upcoming = sum(1 for r in rides_list if r.travel_date >= today and r.status != RideStatus.CANCELLED.value)
    booked = sum(
        1 for r in rides_list
        if any(req.status in ["accepted", "picked_up", "pending"] for req in (r.ride_requests or []))
    )

    items: List[GeneratedRideItem] = []
    for r in rides_list:
        accepted_cnt = sum(1 for req in (r.ride_requests or []) if req.status in ["accepted", "picked_up"])
        has_b = any(req.status in ["accepted", "picked_up", "pending"] for req in (r.ride_requests or []))
        items.append(
            GeneratedRideItem(
                ride_id=r.ride_id,
                travel_date=r.travel_date,
                travel_time=r.travel_time,
                available_seats=r.available_seats,
                status=r.status,
                has_bookings=has_b,
                accepted_bookings_count=accepted_cnt,
            )
        )

    resp = RecurringRideDetailsResponse.model_validate(recurring)
    resp.total_rides = total
    resp.upcoming_rides = upcoming
    resp.booked_rides_count = booked
    resp.schedule_status = _compute_schedule_status(recurring)
    resp.rides = items
    return resp


def update_recurring_ride_service(
    db: Session,
    recurring_ride_id: int,
    update_data: RecurringRideUpdate,
    email: str,
) -> RecurringRideDetailsResponse:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    recurring = recurring_ride_repo.get_recurring_ride_by_id(db, recurring_ride_id, user.id)
    if not recurring:
        raise NotFoundException("Recurring ride schedule not found.")

    # Validate vehicle if updated
    if update_data.vehicle_id and update_data.vehicle_id != recurring.vehicle_id:
        vehicle = vehicle_repo.get_vehicle_by_id(db, update_data.vehicle_id)
        if not vehicle or vehicle.user_id != user.id:
            raise ForbiddenException("Invalid vehicle selected.")
        capacity = vehicle.seating_capacity
    else:
        capacity = recurring.vehicle.seating_capacity if recurring.vehicle else 99

    seats = update_data.available_seats or recurring.available_seats
    if seats > capacity:
        raise BadRequestException(f"Available seats cannot exceed vehicle seating capacity ({capacity}).")

    if update_data.end_date and update_data.end_date < recurring.start_date:
        raise BadRequestException("End date cannot be earlier than schedule start date.")

    # 1. Update schedule record
    recurring_ride_repo.update_recurring_ride(
        db=db,
        recurring_ride=recurring,
        update_data=update_data.model_dump(exclude_unset=True),
    )

    today = date.today()

    # 2. Update future unbooked rides ONLY
    unbooked_future_rides = recurring_ride_repo.get_future_unbooked_rides(db, recurring.id, today)
    for r in unbooked_future_rides:
        if update_data.source:
            r.source = update_data.source
        if update_data.destination:
            r.destination = update_data.destination
        if update_data.route:
            r.route = update_data.route
        if update_data.route_geometry is not None:
            r.route_geometry = update_data.route_geometry
        if update_data.travel_time:
            r.travel_time = update_data.travel_time
        if update_data.available_seats:
            r.available_seats = update_data.available_seats
        if update_data.vehicle_id:
            r.vehicle_id = update_data.vehicle_id

        # If new end_date is before this ride, prune this unbooked ride
        if update_data.end_date and r.travel_date > update_data.end_date:
            db.delete(r)

    # 3. If end_date extended and schedule is active, generate newly added dates
    if recurring.is_active and update_data.end_date and update_data.end_date > recurring.end_date:
        generate_rides_for_schedule(db, recurring, from_date=today, to_date=update_data.end_date)

    db.commit()
    db.refresh(recurring)
    return get_recurring_ride_details_service(db, recurring.id, email)


def pause_recurring_ride_service(
    db: Session,
    recurring_ride_id: int,
    email: str,
) -> RecurringRideResponse:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    recurring = recurring_ride_repo.get_recurring_ride_by_id(db, recurring_ride_id, user.id)
    if not recurring:
        raise NotFoundException("Recurring ride schedule not found.")

    recurring.is_active = False
    db.commit()
    db.refresh(recurring)

    resp = RecurringRideResponse.model_validate(recurring)
    resp.schedule_status = "Paused"
    return resp


def resume_recurring_ride_service(
    db: Session,
    recurring_ride_id: int,
    email: str,
) -> RecurringRideResponse:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    recurring = recurring_ride_repo.get_recurring_ride_by_id(db, recurring_ride_id, user.id)
    if not recurring:
        raise NotFoundException("Recurring ride schedule not found.")

    if recurring.end_date < date.today():
        raise BadRequestException("Cannot resume an expired recurring schedule. Please create a new schedule.")

    recurring.is_active = True
    generate_rides_for_schedule(db, recurring, from_date=date.today())
    db.commit()
    db.refresh(recurring)

    resp = RecurringRideResponse.model_validate(recurring)
    resp.schedule_status = _compute_schedule_status(recurring)
    return resp


def delete_recurring_ride_service(
    db: Session,
    recurring_ride_id: int,
    email: str,
) -> dict:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise NotFoundException("User not found.")

    recurring = recurring_ride_repo.get_recurring_ride_by_id(db, recurring_ride_id, user.id)
    if not recurring:
        raise NotFoundException("Recurring ride schedule not found.")

    today = date.today()
    # Check all associated rides:
    for ride in list(recurring.rides):
        has_bookings = any(
            req.status in ["accepted", "picked_up", "pending"]
            for req in (ride.ride_requests or [])
        )
        if has_bookings or ride.travel_date < today:
            # Preserve booked rides and past rides as independent records
            ride.recurring_ride_id = None
            recurring.rides.remove(ride)

    db.flush()
    recurring_ride_repo.delete_recurring_ride(db, recurring)
    db.commit()

    return {"success": True, "message": "Recurring ride schedule cancelled successfully."}


def sync_all_active_schedules_service(db: Session) -> int:
    """
    Called on server startup / background refresh to idempotently generate
    upcoming rides for all active recurring schedules up to their end dates.
    """
    active_schedules = recurring_ride_repo.get_all_active_recurring_rides(db)
    total_generated = 0
    today = date.today()
    for schedule in active_schedules:
        try:
            cnt = generate_rides_for_schedule(db, schedule, from_date=today)
            total_generated += cnt
        except Exception as e:
            print(f"[RECURRING_RIDE] Error syncing schedule #{schedule.id}: {e}")
            continue

    db.commit()
    return total_generated

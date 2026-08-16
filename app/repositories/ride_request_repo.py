from sqlalchemy.orm import Session,joinedload

from app.models.ride_request import RideRequest
from app.models.ride import Ride


# Get an existing request from a passenger for a ride
def get_request_by_ride_and_passenger(
    db: Session,
    ride_id: int,
    passenger_id: int,
):
    return (
        db.query(RideRequest)
        .filter(
            RideRequest.ride_id == ride_id,
            RideRequest.passenger_id == passenger_id,
        )
        .first()
    )


# Create a new ride request
def create_ride_request(
    db: Session,
    ride_id: int,
    passenger_id: int,
    seats_requested: int,
):
    ride_request = RideRequest(
        ride_id=ride_id,
        passenger_id=passenger_id,
        seats_requested=seats_requested,
        status="pending",
    )

    db.add(ride_request)
    db.commit()
    db.refresh(ride_request)

    return ride_request


# Get all requests for a ride
# Get all requests for a ride owned by the driver
def get_ride_requests(
    db: Session,
    ride_id: int,
    driver_id: int,
):
    return (
        db.query(RideRequest)
        .options(
            joinedload(RideRequest.passenger)
        )
        .join(
            Ride,
            Ride.ride_id == RideRequest.ride_id
        )
        .filter(
            RideRequest.ride_id == ride_id,
            Ride.driver_id == driver_id,
        )
        .order_by(
            RideRequest.created_at.desc()
        )
        .all()
    )
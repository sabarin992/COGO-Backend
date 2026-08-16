from sqlalchemy.orm import Session

from app.models.ride_request import RideRequest


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
from sqlalchemy.orm import Session

from app.models.ride import Ride
from app.schemas.ride import RideCreate


# create ride
def create_ride(
    db: Session,
    ride_data: RideCreate,
    driver_id: int,
):
    ride = Ride(
        driver_id=driver_id,
        vehicle_id=ride_data.vehicle_id,
        source=ride_data.source,
        destination=ride_data.destination,
        route=ride_data.route,
        travel_date=ride_data.travel_date,
        travel_time=ride_data.travel_time,
        available_seats=ride_data.available_seats,
    )

    db.add(ride)
    db.commit()
    db.refresh(ride)

    return ride


# Get all rides posted by a specific driver.
def get_my_rides(db: Session, driver_id: int):
  
    return (
        db.query(Ride)
        .filter(Ride.driver_id == driver_id)
        .order_by(Ride.created_at.desc())
        .all()
    )

# get ride by using vehicle id
def get_ride_by_vehicle_id(db: Session, vehicle_id: int):
    return (
        db.query(Ride)
        .filter(Ride.vehicle_id == vehicle_id)
        .first()
    )


# get ride using rider_id and driver_id
# (We don't want a driver to access another driver's ride. so that i added driver_id)
def get_ride_by_id(db: Session, ride_id: int, driver_id: int):
    return (
        db.query(Ride)
        .filter(
            Ride.ride_id == ride_id,
            Ride.driver_id == driver_id
        )
        .first()
    )


# update ride using ride_id and driver_id
def update_ride(
    db: Session,
    ride_id: int,
    driver_id: int,
    ride_data: dict
):
    ride = (
        db.query(Ride)
        .filter(
            Ride.ride_id == ride_id,
            Ride.driver_id == driver_id
        )
        .first()
    )

    if not ride:
        return None

    for key, value in ride_data.items():
        setattr(ride, key, value)

    db.commit()
    db.refresh(ride)

    return ride


from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.repositories import ride_repo, vehicle_repo
from app.schemas.ride import RideCreate
from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)

from app.repositories import user_repo

def create_ride(
    db: Session,
    ride_data: RideCreate,
    email
):
    # Check whether the vehicle exists
    vehicle = vehicle_repo.get_vehicle_by_id(
        db=db,
        vehicle_id=ride_data.vehicle_id,
    )

    if vehicle is None:
        raise NotFoundException("Vehicle not found.")


    user = user_repo.get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Check whether the vehicle belongs to the logged-in user
    if vehicle.user_id != user.id:
        raise ForbiddenException(
            "You can only post rides using your own vehicle."
        )

    # Validate available seats
    if ride_data.available_seats > vehicle.seating_capacity:
        raise BadRequestException(
            f"Available seats cannot exceed the vehicle seating capacity ({vehicle.seating_capacity})."
        )

    # Create the ride
    ride = ride_repo.create_ride(
        db=db,
        ride_data=ride_data,
        driver_id=user.id,
    )

    return ride



# Get all rides posted by the logged-in driver.
def get_driver_rides_service(db: Session, email):


    driver = user_repo.get_user_by_email(db, email)
    
    if not driver:
        raise NotFoundException("User Not Found")
  

    rides = ride_repo.get_my_rides(db, driver.id)

    if not rides:
        raise NotFoundException("No rides found.")

    return rides
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User

from app.repositories import (
    ride_repo, 
    vehicle_repo
    )

from app.schemas.ride import (
    RideCreate,
    RideUpdate
    )

from app.core.exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
)

from pydantic import EmailStr
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


# Get one ride using ride_id and driver_id
def get_ride_by_id_service(
    db: Session,
    ride_id: int,
    email: EmailStr
):

    user = user_repo.get_user_by_email(db, email)

    if not user:
        raise NotFoundException("User not found.")
    
    ride = ride_repo.get_ride_by_id(
        db=db,
        ride_id=ride_id,
        driver_id=user.id
    )

    if not ride:
        raise NotFoundException("Ride not found.")

    return ride


def update_ride_service(
    db: Session,
    ride_id: int,
    email: EmailStr,
    ride_data: RideUpdate,
):
    user = user_repo.get_user_by_email(db, email)

    if not user:
        raise NotFoundException("User not found.")

    update_data = ride_data.model_dump(exclude_unset=True)

    if not update_data:
        raise BadRequestException("No fields provided for update.")

    ride = ride_repo.update_ride(
        db=db,
        ride_id=ride_id,
        driver_id=user.id,
        ride_data=update_data,
    )

    if not ride:
        raise NotFoundException("Ride not found.")

    return ride



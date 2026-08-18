from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from datetime import datetime, timedelta
from app.schemas.ride import RideDetailsResponse


from app.repositories import (
    ride_repo, 
    vehicle_repo,
    ride_request_repo
    )

from app.schemas.ride import (
    RideCreate,
    RideUpdate,
    RideSearchRequest,
    RideSearchResponse,
     RideRequestCreate
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


# Get complete ride details for a passenger
def get_ride_details_service(
    db: Session,
    ride_id: int,
):
    ride = ride_repo.get_ride_details_by_id(
        db=db,
        ride_id=ride_id,
    )

    if not ride:
        raise NotFoundException(
            "Ride not found."
        )

    passengers = []

    for request in ride.ride_requests:
        passengers.append(
            {
                "id": request.passenger.id,
                "full_name": request.passenger.full_name,
                "profile_pic": request.passenger.profile_pic,
                "seats_requested": request.seats_requested,
            }
        )

    return RideDetailsResponse(
        ride_id=ride.ride_id,

        source=ride.source,
        destination=ride.destination,
        route=ride.route,

        travel_date=ride.travel_date,
        travel_time=ride.travel_time,

        available_seats=ride.available_seats,

        driver={
            "id": ride.driver.id,
            "full_name": ride.driver.full_name,
            "profile_pic": ride.driver.profile_pic,
        },

        vehicle={
            "id": ride.vehicle.id,
            "vehicle_type": ride.vehicle.vehicle_type,
            "brand": ride.vehicle.brand,
            "model": ride.vehicle.model,
            "year": ride.vehicle.year,
            "color": ride.vehicle.color,
            "registration_number": ride.vehicle.registration_number,
            "seating_capacity": ride.vehicle.seating_capacity,
        },

        passengers=passengers,
    )


# Edit ride
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


# Delete the ride
def delete_ride_service(
    db: Session,
    ride_id: int,
    email: EmailStr,
):
    user = user_repo.get_user_by_email(db, email)

    if not user:
        raise NotFoundException("User not found.")

    ride = ride_repo.delete_ride(
        db=db,
        ride_id=ride_id,
        driver_id=user.id,
    )

    if not ride:
        raise NotFoundException("Ride not found.")

    return ride


# Search rides
def search_rides_service(
    db: Session,
    search_data: RideSearchRequest,
):
    start_time = None
    end_time = None

    if search_data.travel_time:
        requested_datetime = datetime.combine(
            search_data.travel_date,
            search_data.travel_time,
        )

        start_datetime = (
            requested_datetime - timedelta(minutes=30)
        )

        end_datetime = (
            requested_datetime + timedelta(minutes=30)
        )

        start_time = start_datetime.time()
        end_time = end_datetime.time()

    rides = ride_repo.search_rides(
        db=db,
        search_data=search_data,
        start_time=start_time,
        end_time=end_time,
    )

    if not rides:
        raise NotFoundException(
            "No rides found matching your search."
        )

    response = []

    for ride, driver, vehicle in rides:
        response.append(
            RideSearchResponse(
                ride_id=ride.ride_id,

                source=ride.source,
                destination=ride.destination,

                travel_date=ride.travel_date,
                travel_time=ride.travel_time,

                available_seats=ride.available_seats,

                driver_id=driver.id,
                driver_name=driver.full_name,
                driver_profile_pic=driver.profile_pic,

                vehicle_id=vehicle.id,
                vehicle_type=vehicle.vehicle_type,
                vehicle_brand=vehicle.brand,
                vehicle_model=vehicle.model,
                vehicle_color=vehicle.color,
            )
        )

    return response



# Create a ride request
def create_ride_request_service(
    db: Session,
    request_data: RideRequestCreate,
    email: EmailStr,
):

    user = user_repo.get_user_by_email(db, email)
    
    if not user:
        raise NotFoundException("User not found.")

    passenger_id = user.id

    # Get the ride
    ride = ride_repo.get_ride_details_by_id(
        db=db,
        ride_id=request_data.ride_id,
    )

    if not ride:
        raise NotFoundException(
            "Ride not found."
        )

    # Passenger cannot request their own ride
    if ride.driver_id == passenger_id:
        raise BadRequestException(
            "You cannot request your own ride."
        )

    # Validate requested seats
    if request_data.seats_requested > ride.available_seats:
        raise BadRequestException(
            "Requested seats exceed available seats."
        )

    # Check whether passenger already requested this ride
    existing_request = (
        ride_request_repo.get_request_by_ride_and_passenger(
            db=db,
            ride_id=request_data.ride_id,
            passenger_id=passenger_id,
        )
    )

    if existing_request:
        raise BadRequestException(
            "You have already requested this ride."
        )

    # Create request
    ride_request = ride_request_repo.create_ride_request(
        db=db,
        ride_id=request_data.ride_id,
        passenger_id=passenger_id,
        seats_requested=request_data.seats_requested,
    )

    return {
        "ride_request_id": ride_request.ride_request_id,
        "ride_id": ride_request.ride_id,
        "passenger_id": ride_request.passenger_id,
        "passenger_name": user.full_name,
        "passenger_profile_pic": user.profile_pic,
        "seats_requested": ride_request.seats_requested,
        "status": ride_request.status,
        "created_at": ride_request.created_at,
    }



# Get all ride requests for a ride owned by the logged-in driver.
def get_ride_requests_service(
    db: Session,
    ride_id: int,
    email: EmailStr,
):
    # Get logged-in driver
    driver = user_repo.get_user_by_email(
        db=db,
        email=email,
    )

    if not driver:
        raise NotFoundException(
            "User not found."
        )

    # Check whether the ride belongs to this driver
    ride = ride_repo.get_ride_by_id(
        db=db,
        ride_id=ride_id,
        driver_id=driver.id,
    )

    if not ride:
        raise NotFoundException(
            "Ride not found."
        )

    # Get ride requests
    requests = ride_request_repo.get_ride_requests(
        db=db,
        ride_id=ride_id,
        driver_id=driver.id,
    )

    # Convert database objects into response data
    return [
        {
            "ride_request_id": request.ride_request_id,
            "ride_id": request.ride_id,
            "passenger_id": request.passenger_id,
            "passenger_name": request.passenger.full_name,
            "passenger_profile_pic": request.passenger.profile_pic,
            "seats_requested": request.seats_requested,
            "status": request.status,
            "created_at": request.created_at,
        }
        for request in requests
    ]


# Accept a ride request
def accept_ride_request_service(
    db: Session,
    ride_request_id: int,
    email: EmailStr,
):
    try:
        # Get logged-in driver
        driver = user_repo.get_user_by_email(
            db=db,
            email=email,
        )

        if not driver:
            raise NotFoundException(
                "User not found."
            )

        # Get ride request
        ride_request = (
            ride_request_repo.get_ride_request_by_id(
                db=db,
                ride_request_id=ride_request_id,
            )
        )

        if not ride_request:
            raise NotFoundException(
                "Ride request not found."
            )

        # Verify that the ride belongs to the driver
        ride = ride_repo.get_ride_by_id(
            db=db,
            ride_id=ride_request.ride_id,
            driver_id=driver.id,
        )

        if not ride:
            raise ForbiddenException(
                "You are not allowed to manage this ride request."
            )

        # Request must still be pending
        if ride_request.status != "pending":
            raise BadRequestException(
                "This ride request has already been processed."
            )

        # Lock the ride and reduce available seats
        ride = ride_repo.reduce_available_seats(
            db=db,
            ride_id=ride_request.ride_id,
            seats=ride_request.seats_requested,
        )

        if not ride:
            raise BadRequestException(
                "Not enough seats available."
            )

        # Accept the request
        updated_request = (
            ride_request_repo.update_ride_request_status(
                db=db,
                ride_request_id=ride_request_id,
                status="accepted",
            )
        )

        # Commit both changes together
        db.commit()
        db.refresh(updated_request)

        return {
            "ride_request_id": updated_request.ride_request_id,
            "ride_id": updated_request.ride_id,
            "passenger_id": updated_request.passenger_id,
            "passenger_name": updated_request.passenger.full_name if updated_request.passenger else None,
            "passenger_profile_pic": updated_request.passenger.profile_pic if updated_request.passenger else None,
            "seats_requested": updated_request.seats_requested,
            "status": updated_request.status,
            "created_at": updated_request.created_at,
        }

    except Exception:
        db.rollback()
        raise


# Reject a ride request
def reject_ride_request_service(
    db: Session,
    ride_request_id: int,
    email: EmailStr,
):
    # Get logged-in driver
    driver = user_repo.get_user_by_email(
        db=db,
        email=email,
    )

    if not driver:
        raise NotFoundException(
            "User not found."
        )

    # Get ride request
    ride_request = ride_request_repo.get_ride_request_by_id(
        db=db,
        ride_request_id=ride_request_id,
    )

    if not ride_request:
        raise NotFoundException(
            "Ride request not found."
        )

    # Verify ride belongs to driver
    ride = ride_repo.get_ride_by_id(
        db=db,
        ride_id=ride_request.ride_id,
        driver_id=driver.id,
    )

    if not ride:
        raise ForbiddenException(
            "You are not allowed to manage this ride request."
        )

    # Request must still be pending
    if ride_request.status != "pending":
        raise BadRequestException(
            "This ride request has already been processed."
        )

    # Reject request
    updated_request = (
        ride_request_repo.update_ride_request_status(
            db=db,
            ride_request_id=ride_request_id,
            status="rejected",
        )
    )

    return {
        "ride_request_id": updated_request.ride_request_id,
        "ride_id": updated_request.ride_id,
        "passenger_id": updated_request.passenger_id,
        "passenger_name": updated_request.passenger.full_name if updated_request.passenger else None,
        "passenger_profile_pic": updated_request.passenger.profile_pic if updated_request.passenger else None,
        "seats_requested": updated_request.seats_requested,
        "status": updated_request.status,
        "created_at": updated_request.created_at,
    }




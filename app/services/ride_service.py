from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.user import User
from app.models.ride import RideStatus
from datetime import datetime, timedelta
from app.schemas.ride import RideDetailsResponse
from app.utils.route_utils import is_intermediate_route
from app.services.chat_service import get_or_create_conversation


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

    # Only users with the Rider role can post a ride
    if user.role != "rider":
        raise ForbiddenException(
            "Only users with the Rider role can post a ride."
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
                "ride_request_id": request.ride_request_id,
                "full_name": request.passenger.full_name,
                "profile_pic": request.passenger.profile_pic,
                "seats_requested": request.seats_requested,
                "status": request.status,
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
        status=ride.status,

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

    # -----------------------------------------
    # Calculate ±30 minute time range
    # -----------------------------------------
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

    # -----------------------------------------
    # Get candidate rides from repository
    # -----------------------------------------
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

    # -----------------------------------------
    # Intermediate route filtering
    # -----------------------------------------
    matched_rides = []

    for ride, driver, vehicle in rides:

        # Make sure route geometry exists
        if not ride.route_geometry:
            continue

        result = is_intermediate_route(
            passenger_source=search_data.source_coords,
            passenger_destination=search_data.destination_coords,
            route_coordinates=ride.route_geometry,
        )

        print("\n================================")
        print("Checking ride:", ride.ride_id)
        print("Rider source:", ride.source)
        print("Rider destination:", ride.destination)

        print(
            "Passenger source near route:",
            result["source_near_route"]
        )

        print(
            "Passenger destination near route:",
            result["destination_near_route"]
        )

        print(
            "Correct order:",
            result["correct_order"]
        )

        print(
            "Intermediate route:",
            result["is_match"]
        )

        print("================================\n")

        # Only keep rides where passenger journey
        # is an intermediate part of rider's route
        if result["is_match"]:
            matched_rides.append(
                (ride, driver, vehicle)
            )

    # -----------------------------------------
    # No intermediate rides found
    # -----------------------------------------
    if not matched_rides:
        raise NotFoundException(
            "No rides found matching your route."
        )

    # -----------------------------------------
    # Create response
    # -----------------------------------------
    response = []

    for ride, driver, vehicle in matched_rides:

        response.append(
            RideSearchResponse(
                ride_id=ride.ride_id,

                source=ride.source,
                destination=ride.destination,

                travel_date=ride.travel_date,
                travel_time=ride.travel_time,

                available_seats=ride.available_seats,
                status=ride.status,

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

    # # Check whether passenger already requested this ride
    # existing_request = (
    #     ride_request_repo.get_request_by_ride_and_passenger(
    #         db=db,
    #         ride_id=request_data.ride_id,
    #         passenger_id=passenger_id,
    #     )
    # )

    # if existing_request:
    #     raise BadRequestException(
    #         "You have already requested this ride."
    #     )

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



def format_ride_request_dict(request):
    passenger_name = request.passenger.full_name if request.passenger else None
    passenger_pic = request.passenger.profile_pic if request.passenger else None

    ride_source = request.ride.source if request.ride else None
    ride_dest = request.ride.destination if request.ride else None
    ride_date = request.ride.travel_date if request.ride else None
    ride_time = request.ride.travel_time if request.ride else None
    ride_seats = request.ride.available_seats if request.ride else None
    ride_route = request.ride.route if request.ride else None
    ride_status = request.ride.status if request.ride else None

    driver_name = request.ride.driver.full_name if (request.ride and request.ride.driver) else None
    driver_pic = request.ride.driver.profile_pic if (request.ride and request.ride.driver) else None

    return {
        "ride_request_id": request.ride_request_id,
        "ride_id": request.ride_id,
        "passenger_id": request.passenger_id,
        "passenger_name": passenger_name,
        "passenger_profile_pic": passenger_pic,
        "seats_requested": request.seats_requested,
        "status": request.status,
        "created_at": request.created_at,
        "source": ride_source,
        "destination": ride_dest,
        "travel_date": ride_date,
        "travel_time": ride_time,
        "available_seats": ride_seats,
        "route": ride_route,
        "ride_status": ride_status,
        "driver_name": driver_name,
        "driver_profile_pic": driver_pic,
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

    return [format_ride_request_dict(req) for req in requests]


# Get all incoming requests across ALL rides posted by the logged-in driver
def get_all_my_ride_requests_service(
    db: Session,
    email: EmailStr,
):
    driver = user_repo.get_user_by_email(db=db, email=email)
    if not driver:
        raise NotFoundException("User not found.")

    requests = ride_request_repo.get_all_driver_ride_requests(
        db=db,
        driver_id=driver.id,
    )

    return [format_ride_request_dict(req) for req in requests]


# Get all ride requests sent by the logged-in user as a passenger (My Bookings)
def get_all_my_bookings_service(
    db: Session,
    email: EmailStr,
):
    passenger = user_repo.get_user_by_email(db=db, email=email)
    if not passenger:
        raise NotFoundException("User not found.")

    requests = ride_request_repo.get_passenger_ride_requests(
        db=db,
        passenger_id=passenger.id,
    )

    return [format_ride_request_dict(req) for req in requests]


# Cancel a ride request created by the logged-in passenger
def cancel_ride_request_service(
    db: Session,
    ride_request_id: int,
    email: EmailStr,
):
    passenger = user_repo.get_user_by_email(db=db, email=email)
    if not passenger:
        raise NotFoundException("User not found.")

    request = ride_request_repo.get_ride_request_by_id(
        db=db,
        ride_request_id=ride_request_id,
    )

    if not request:
        raise NotFoundException("Ride request not found.")

    if request.passenger_id != passenger.id:
        raise ForbiddenException("You are not allowed to cancel this request.")

    if request.status in ["rejected", "cancelled"]:
        raise BadRequestException(f"This ride request is already {request.status}.")

    # If status was accepted, restore seats to the ride
    if request.status == "accepted" and request.ride:
        request.ride.available_seats += request.seats_requested

    updated_request = ride_request_repo.update_ride_request_status(
        db=db,
        ride_request_id=ride_request_id,
        status="cancelled",
    )



    db.commit()
    db.refresh(updated_request)

    return format_ride_request_dict(updated_request)



# Get details for a specific ride request by ID
def get_single_ride_request_details_service(
    db: Session,
    ride_request_id: int,
    email: EmailStr,
):
    driver = user_repo.get_user_by_email(db=db, email=email)
    if not driver:
        raise NotFoundException("User not found.")

    request = ride_request_repo.get_ride_request_by_id(
        db=db,
        ride_request_id=ride_request_id,
    )

    if not request:
        raise NotFoundException("Ride request not found.")

    if request.ride and (request.ride.driver_id != driver.id and request.passenger_id != driver.id):
        raise ForbiddenException("You are not authorized to view this request.")

    return format_ride_request_dict(request)


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

        # Check allowed ride status for accepting requests
        allowed_statuses = [RideStatus.CREATED, RideStatus.UPCOMING]
        if ride.status not in allowed_statuses:
            raise BadRequestException(
                f"Cannot accept ride requests when ride status is '{ride.status}'."
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

        # Transition Ride status CREATED -> UPCOMING if needed
        if ride.status == RideStatus.CREATED:
            ride = ride_repo.update_ride_status(
                db=db,
                ride_id=ride.ride_id,
                status=RideStatus.UPCOMING.value,
            )

        # Accept the request
        updated_request = (
            ride_request_repo.update_ride_request_status(
                db=db,
                ride_request_id=ride_request_id,
                status="accepted",
            )
        )
        # Create chat conversation between driver and passenger
        get_or_create_conversation(
            db=db,
            ride_id=ride_request.ride_id,
            driver_id=driver.id,
            passenger_id=ride_request.passenger_id,
        )

        # Commit all changes together
        db.commit()
        db.refresh(updated_request)

        return format_ride_request_dict(updated_request)

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

    db.commit()
    db.refresh(updated_request)

    return format_ride_request_dict(updated_request)


# Start a ride (UPCOMING -> STARTED)
def start_ride_service(
    db: Session,
    ride_id: int,
    email: EmailStr,
):
    try:
        # Get logged-in user
        user = user_repo.get_user_by_email(db=db, email=email)
        if not user:
            raise NotFoundException("User not found.")

        # Get ride by ID
        ride = ride_repo.get_ride_by_id_only(db=db, ride_id=ride_id)
        if not ride:
            raise NotFoundException("Ride not found.")

        # Verify current logged-in user is the driver/owner of the ride
        if ride.driver_id != user.id:
            raise ForbiddenException("You are not allowed to start this ride.")

        # Only allow transition from UPCOMING -> STARTED
        if ride.status != RideStatus.UPCOMING:
            raise BadRequestException(
                f"Cannot start a ride with status '{ride.status}'. Only rides in UPCOMING status can be started."
            )

        # Update ride status to STARTED
        updated_ride = ride_repo.update_ride_status(
            db=db,
            ride_id=ride_id,
            status=RideStatus.STARTED.value,
        )

        db.commit()
        db.refresh(updated_ride)

        return updated_ride

    except Exception:
        db.rollback()
        raise


# Mark ride as reached pickup point (STARTED -> REACHED_PICKUP)
def reached_pickup_service(
    db: Session,
    ride_id: int,
    email: EmailStr,
):
    try:
        # Get logged-in user
        user = user_repo.get_user_by_email(db=db, email=email)
        if not user:
            raise NotFoundException("User not found.")

        # Get ride by ID
        ride = ride_repo.get_ride_by_id_only(db=db, ride_id=ride_id)
        if not ride:
            raise NotFoundException("Ride not found.")

        # Verify current logged-in user is the driver/owner of the ride
        if ride.driver_id != user.id:
            raise ForbiddenException("You are not allowed to manage this ride.")

        # Only allow transition from STARTED -> REACHED_PICKUP
        if ride.status != RideStatus.STARTED:
            raise BadRequestException(
                f"Cannot mark pickup reached for a ride with status '{ride.status}'. Only rides in STARTED status can transition to REACHED_PICKUP."
            )

        # Update ride status to REACHED_PICKUP
        updated_ride = ride_repo.update_ride_status(
            db=db,
            ride_id=ride_id,
            status=RideStatus.REACHED_PICKUP.value,
        )

        db.commit()
        db.refresh(updated_ride)

        return updated_ride

    except Exception:
        db.rollback()
        raise


# Passenger pickup service (RideRequest: accepted -> picked_up, Ride: REACHED_PICKUP -> ONGOING)
def pickup_passenger_service(
    db: Session,
    ride_id: int,
    ride_request_id: int,
    email: EmailStr,
):
    try:
        # Get logged-in user (driver)
        driver = user_repo.get_user_by_email(db=db, email=email)
        if not driver:
            raise NotFoundException("User not found.")

        # Validate Ride exists
        ride = ride_repo.get_ride_by_id_only(db=db, ride_id=ride_id)
        if not ride:
            raise NotFoundException("Ride not found.")

        # Validate RideRequest exists
        ride_request = ride_request_repo.get_ride_request_by_id(
            db=db,
            ride_request_id=ride_request_id,
        )
        if not ride_request:
            raise NotFoundException("Ride request not found.")

        # Validate RideRequest belongs to the specified ride_id
        if ride_request.ride_id != ride_id:
            raise BadRequestException("This ride request does not belong to the specified ride.")

        # Verify current logged-in user is the driver/owner of the ride
        if ride.driver_id != driver.id:
            raise ForbiddenException("You are not allowed to manage this ride.")

        # Validate Ride status: Must be REACHED_PICKUP or ONGOING
        allowed_ride_statuses = [RideStatus.REACHED_PICKUP, RideStatus.ONGOING]
        if ride.status not in allowed_ride_statuses:
            raise BadRequestException(
                f"Cannot pick up passenger when ride status is '{ride.status}'. Only rides in REACHED_PICKUP or ONGOING status can perform passenger pickup."
            )

        # Validate RideRequest status: Must be accepted
        if ride_request.status != "accepted":
            raise BadRequestException(
                f"Cannot pick up passenger when request status is '{ride_request.status}'. Only accepted requests can be picked up."
            )

        # Update RideRequest status: accepted -> picked_up
        updated_request = ride_request_repo.update_ride_request_status(
            db=db,
            ride_request_id=ride_request_id,
            status="picked_up",
        )

        # Update Ride status: REACHED_PICKUP -> ONGOING if needed
        if ride.status == RideStatus.REACHED_PICKUP:
            ride_repo.update_ride_status(
                db=db,
                ride_id=ride_id,
                status=RideStatus.ONGOING.value,
            )

        # Commit both updates together in the same transaction
        db.commit()
        db.refresh(updated_request)

        return format_ride_request_dict(updated_request)

    except Exception:
        db.rollback()
        raise


# Complete a ride (ONGOING -> COMPLETED)
def complete_ride_service(
    db: Session,
    ride_id: int,
    email: EmailStr,
):
    try:
        # Get logged-in user (driver)
        driver = user_repo.get_user_by_email(db=db, email=email)
        if not driver:
            raise NotFoundException("User not found.")

        # Get ride by ID
        ride = ride_repo.get_ride_by_id_only(db=db, ride_id=ride_id)
        if not ride:
            raise NotFoundException("Ride not found.")

        # Verify current logged-in user is the driver/owner of the ride
        if ride.driver_id != driver.id:
            raise ForbiddenException("You are not allowed to manage this ride.")

        # Only allow transition from ONGOING -> COMPLETED
        if ride.status != RideStatus.ONGOING:
            raise BadRequestException(
                f"Cannot complete ride with status '{ride.status}'. Only rides in ONGOING status can be completed."
            )

        # Update ride status to COMPLETED
        updated_ride = ride_repo.update_ride_status(
            db=db,
            ride_id=ride_id,
            status=RideStatus.COMPLETED.value,
        )

        db.commit()
        db.refresh(updated_ride)

        return updated_ride

    except Exception:
        db.rollback()
        raise









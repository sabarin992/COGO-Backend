from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services import ride_service
from pydantic import EmailStr
from typing import List

from app.schemas.ride import (
    RideCreate,
    RideResponse,
    RideUpdate,
    RideSearchRequest,
    RideSearchResponse,
    RideDetailsResponse,
    RideRequestCreate,
    RideRequestResponse,
)




router = APIRouter()

# create ride
@router.post(
    "/",
    response_model=RideResponse,
    status_code=201,
)
def create_ride(
    ride_data: RideCreate,
    db: Session = Depends(get_db),
    email = Depends(get_current_user),
):
    ride = ride_service.create_ride(
        db=db,
        ride_data=ride_data,
        email=email,
    )

    return ride

# Get all loggedin user ride
@router.get(
    "/my-rides",
    response_model=list[RideResponse],
)
def get_my_rides(
    db: Session = Depends(get_db),
    email = Depends(get_current_user),
):
    return ride_service.get_driver_rides_service(
        db=db,
        email=email,
    )


# Get all ride requests received for rides posted by the logged-in driver.
@router.get(
    "/my-requests",
    response_model=List[RideRequestResponse],
)
def get_all_my_ride_requests(
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ride_service.get_all_my_ride_requests_service(
        db=db,
        email=email,
    )


# Get single ride request details by ID
@router.get(
    "/requests/{ride_request_id}",
    response_model=RideRequestResponse,
)
def get_single_ride_request_details(
    ride_request_id: int,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ride_service.get_single_ride_request_details_service(
        db=db,
        ride_request_id=ride_request_id,
        email=email,
    )


# Get one ride for rider
@router.get("/{ride_id}",response_model=RideResponse)
def get_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    email = Depends(get_current_user),
):
    return ride_service.get_ride_by_id_service(
        db=db,
        ride_id=ride_id,
        email = email,
    )


# get ride for passenger
@router.get(
    "/{ride_id}/details",
    response_model=RideDetailsResponse,
)
def get_ride_details(
    ride_id: int,
    db: Session = Depends(get_db),
):
    return ride_service.get_ride_details_service(
        db=db,
        ride_id=ride_id,
    )

# Edit ride
@router.put("/{ride_id}",response_model=RideResponse)
def update_ride(
    ride_id: int,
    ride_data: RideUpdate,
    db: Session = Depends(get_db),
    email=Depends(get_current_user),
):
    
    return ride_service.update_ride_service(
        db=db,
        ride_id=ride_id,
        email=email,
        ride_data=ride_data,
    )


# Delete ride
@router.delete("/{ride_id}")
def delete_ride(
    ride_id: int,
    db: Session = Depends(get_db),
    email=Depends(get_current_user),
):
    return ride_service.delete_ride_service(
        db=db,
        ride_id=ride_id,
        email=email,
    )


@router.post(
    "/search",
    response_model=list[RideSearchResponse]
)
def search_rides(
    search_data: RideSearchRequest,
    db: Session = Depends(get_db),
    email=Depends(get_current_user),
):
    print(search_data)
    return ride_service.search_rides_service(
        db=db,
        search_data=search_data,
    )

# ride request
@router.post(
    "/request",
    response_model=RideRequestResponse,
)
def create_ride_request(
    request_data: RideRequestCreate,
    db: Session = Depends(get_db),
    email = Depends(get_current_user),
):
    return ride_service.create_ride_request_service(
        db=db,
        request_data=request_data,
        email=email,
    )

# Get all ride requests for a ride owned by the logged-in driver.
@router.get(
    "/{ride_id}/requests",
    response_model=List[RideRequestResponse],
)
def get_ride_requests(
    ride_id: int,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ride_service.get_ride_requests_service(
        db=db,
        ride_id=ride_id,
        email=email,
    )



# Accept a pending ride request.
@router.post(
    "/requests/{ride_request_id}/accept",
    response_model=RideRequestResponse,
)
def accept_ride_request(
    ride_request_id: int,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ride_service.accept_ride_request_service(
        db=db,
        ride_request_id=ride_request_id,
        email=email,
    )

# Reject a pending ride request.
@router.post(
    "/requests/{ride_request_id}/reject",
    response_model=RideRequestResponse,
)
def reject_ride_request(
    ride_request_id: int,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ride_service.reject_ride_request_service(
        db=db,
        ride_request_id=ride_request_id,
        email=email,
    )
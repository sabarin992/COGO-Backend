from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services import ride_service

from app.schemas.ride import (
    RideCreate,
    RideResponse,
)




router = APIRouter()


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



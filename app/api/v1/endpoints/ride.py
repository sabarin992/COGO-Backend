from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user

from app.models.user import User

from app.schemas.ride import (
    RideCreate,
    RideResponse,
)

from app.services import ride_service


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
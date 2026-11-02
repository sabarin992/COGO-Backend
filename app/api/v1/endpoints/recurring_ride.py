from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.schemas.recurring_ride import (
    RecurringRideCreate,
    RecurringRideUpdate,
    RecurringRideResponse,
    RecurringRideDetailsResponse,
)
from app.services import recurring_ride_service

router = APIRouter()


@router.post(
    "",
    response_model=RecurringRideDetailsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recurring ride schedule and generate initial rides",
)
@router.post(
    "/",
    response_model=RecurringRideDetailsResponse,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_recurring_ride(
    ride_data: RecurringRideCreate,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.create_recurring_ride(
        db=db,
        ride_data=ride_data,
        email=email,
    )


@router.get(
    "",
    response_model=List[RecurringRideResponse],
    summary="Get all recurring ride schedules for the logged-in driver",
)
@router.get(
    "/",
    response_model=List[RecurringRideResponse],
    include_in_schema=False,
)
def get_my_recurring_rides(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.get_driver_recurring_rides_service(
        db=db,
        email=email,
    )


@router.get(
    "/{recurring_ride_id}",
    response_model=RecurringRideDetailsResponse,
    summary="Get details of a specific recurring ride schedule",
)
def get_recurring_ride_details(
    recurring_ride_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.get_recurring_ride_details_service(
        db=db,
        recurring_ride_id=recurring_ride_id,
        email=email,
    )


@router.put(
    "/{recurring_ride_id}",
    response_model=RecurringRideDetailsResponse,
    summary="Update recurring ride schedule and update future unbooked rides",
)
def update_recurring_ride(
    recurring_ride_id: int,
    update_data: RecurringRideUpdate,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.update_recurring_ride_service(
        db=db,
        recurring_ride_id=recurring_ride_id,
        update_data=update_data,
        email=email,
    )


@router.patch(
    "/{recurring_ride_id}/pause",
    response_model=RecurringRideResponse,
    summary="Pause a recurring ride schedule",
)
def pause_recurring_ride(
    recurring_ride_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.pause_recurring_ride_service(
        db=db,
        recurring_ride_id=recurring_ride_id,
        email=email,
    )


@router.patch(
    "/{recurring_ride_id}/resume",
    response_model=RecurringRideResponse,
    summary="Resume a paused recurring ride schedule and generate missing upcoming rides",
)
def resume_recurring_ride(
    recurring_ride_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.resume_recurring_ride_service(
        db=db,
        recurring_ride_id=recurring_ride_id,
        email=email,
    )


@router.delete(
    "/{recurring_ride_id}",
    summary="Cancel a recurring ride schedule (preserves booked rides as independent rides)",
)
def delete_recurring_ride(
    recurring_ride_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return recurring_ride_service.delete_recurring_ride_service(
        db=db,
        recurring_ride_id=recurring_ride_id,
        email=email,
    )

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.services import admin_ride_service
from app.schemas.admin_ride import (
    AdminRideListResponse,
    AdminRideStatsResponse,
    AdminRideDetailsResponse,
    AdminRideCancelRequest,
)

router = APIRouter()


@router.get(
    "/statistics",
    response_model=AdminRideStatsResponse,
    summary="Get aggregated ride statistics for admin dashboard",
)
def get_admin_ride_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_ride_service.get_admin_ride_stats_service(db=db)


@router.get(
    "",
    response_model=AdminRideListResponse,
    summary="List all rides with search, filtering and server-side pagination for admin",
)
def get_admin_rides(
    search: Optional[str] = Query(None, description="Search by ride ID, driver name, driver email, source, destination"),
    status: Optional[str] = Query(None, description="Filter by ride status"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_ride_service.get_admin_rides_service(
        db=db,
        search=search,
        status=status,
        page=page,
        size=size,
    )


@router.get(
    "/{ride_id}",
    response_model=AdminRideDetailsResponse,
    summary="Get comprehensive ride details for admin",
)
def get_admin_ride_details(
    ride_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_ride_service.get_admin_ride_details_service(
        db=db,
        ride_id=ride_id,
    )


@router.post(
    "/{ride_id}/cancel",
    response_model=AdminRideDetailsResponse,
    summary="Cancel a ride as an admin with a mandatory cancellation reason",
)
def cancel_admin_ride(
    ride_id: int,
    cancel_data: AdminRideCancelRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_ride_service.admin_cancel_ride_service(
        db=db,
        ride_id=ride_id,
        admin_id=admin.id,
        reason=cancel_data.reason,
    )


from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_admin
from app.models.user import User
from app.services import admin_booking_service
from app.schemas.admin_booking import (
    AdminBookingListResponse,
    AdminBookingStatsResponse,
    AdminBookingDetailsResponse,
    AdminBookingCancelRequest,
)

router = APIRouter()


@router.get(
    "/statistics",
    response_model=AdminBookingStatsResponse,
    summary="Get aggregated booking and ride request statistics for admin dashboard",
)
def get_admin_booking_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_booking_service.get_admin_booking_stats_service(db=db)


@router.get(
    "",
    response_model=AdminBookingListResponse,
    summary="List all bookings/ride requests with search, filtering and server-side pagination for admin",
)
def get_admin_bookings(
    search: Optional[str] = Query(None, description="Search by booking ID, passenger name/email, driver name/email, route"),
    status: Optional[str] = Query(None, description="Filter by booking status (pending, accepted, rejected, cancelled)"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_booking_service.get_admin_bookings_service(
        db=db,
        search=search,
        status=status,
        page=page,
        size=size,
    )


@router.get(
    "/{booking_id}",
    response_model=AdminBookingDetailsResponse,
    summary="Get comprehensive booking details for admin",
)
def get_admin_booking_details(
    booking_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_booking_service.get_admin_booking_details_service(
        db=db,
        booking_id=booking_id,
    )


@router.post(
    "/{booking_id}/cancel",
    response_model=AdminBookingDetailsResponse,
    summary="Cancel a booking as an admin with a mandatory cancellation reason",
)
def cancel_admin_booking(
    booking_id: int,
    cancel_data: AdminBookingCancelRequest,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    return admin_booking_service.admin_cancel_booking_service(
        db=db,
        booking_id=booking_id,
        admin_id=admin.id,
        reason=cancel_data.reason,
    )


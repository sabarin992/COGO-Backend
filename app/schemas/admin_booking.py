from datetime import datetime, date, time
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


class AdminBookingPassenger(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_pic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminBookingDriver(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_pic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminBookingRide(BaseModel):
    ride_id: int
    source: str
    destination: str
    travel_date: date
    travel_time: time
    available_seats: int
    status: str

    model_config = ConfigDict(from_attributes=True)


class AdminBookingVehicle(BaseModel):
    id: int
    vehicle_type: str
    brand: str
    model: str
    year: Optional[int] = None
    color: Optional[str] = None
    registration_number: str

    model_config = ConfigDict(from_attributes=True)


class AdminBookingListItem(BaseModel):
    booking_id: int
    ride_id: int
    passenger_id: int
    passenger_name: str
    passenger_email: Optional[str] = None
    passenger_profile_pic: Optional[str] = None
    driver_id: int
    driver_name: str
    driver_email: Optional[str] = None
    driver_profile_pic: Optional[str] = None
    source: str
    destination: str
    travel_date: date
    travel_time: time
    seats_requested: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminBookingListResponse(BaseModel):
    items: List[AdminBookingListItem]
    total: int
    page: int
    size: int
    pages: int


class AdminBookingStatsResponse(BaseModel):
    total: int
    pending: int
    accepted: int
    rejected: int
    cancelled: int


class AdminBookingDetailsResponse(BaseModel):
    booking_id: int
    status: str
    seats_requested: int
    cancellation_reason: Optional[str] = None
    cancelled_by_admin: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    passenger: AdminBookingPassenger
    driver: AdminBookingDriver
    ride: AdminBookingRide
    vehicle: Optional[AdminBookingVehicle] = None


class AdminBookingCancelRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Mandatory cancellation reason")


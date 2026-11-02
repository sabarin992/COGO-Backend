from datetime import datetime, date, time
from typing import Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class AdminRideDriver(BaseModel):
    id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_pic: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class AdminRideVehicle(BaseModel):
    id: int
    vehicle_type: str
    brand: str
    model: str
    year: int
    color: str
    registration_number: str
    seating_capacity: int
    images: Optional[Any] = None

    model_config = ConfigDict(from_attributes=True)


class AdminRidePassenger(BaseModel):
    passenger_id: int
    ride_request_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_pic: Optional[str] = None
    seats_requested: int
    status: str
    created_at: Optional[datetime] = None


class AdminRideRequestItem(BaseModel):
    ride_request_id: int
    passenger_id: int
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    profile_pic: Optional[str] = None
    seats_requested: int
    status: str
    created_at: Optional[datetime] = None


class AdminRideListItem(BaseModel):
    ride_id: int
    driver_id: int
    driver_name: str
    driver_email: Optional[str] = None
    driver_profile_pic: Optional[str] = None
    source: str
    destination: str
    travel_date: date
    travel_time: time
    available_seats: int
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminRideListResponse(BaseModel):
    items: List[AdminRideListItem]
    total: int
    page: int
    size: int
    pages: int


class AdminRideStatsResponse(BaseModel):
    total: int
    created: int
    upcoming: int
    started: int
    reached_pickup: int
    ongoing: int
    completed: int
    cancelled: int


class AdminRideDetailsResponse(BaseModel):
    ride_id: int
    source: str
    destination: str
    route: Optional[str] = None
    route_geometry: Optional[Any] = None
    travel_date: date
    travel_time: time
    available_seats: int
    status: str
    cancellation_reason: Optional[str] = None
    cancelled_by_admin: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    driver: AdminRideDriver
    vehicle: AdminRideVehicle
    passengers: List[AdminRidePassenger] = []
    requests: List[AdminRideRequestItem] = []


class AdminRideCancelRequest(BaseModel):
    reason: str = Field(..., min_length=1, description="Mandatory cancellation reason")


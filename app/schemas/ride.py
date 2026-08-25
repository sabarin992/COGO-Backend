from datetime import datetime, date, time

from pydantic import BaseModel, Field, ConfigDict

from app.models.ride import RideStatus


class RideCreate(BaseModel):
    vehicle_id: int

    source: str
    destination: str
    route: str | None = None

    travel_date: date
    travel_time: time

    available_seats: int = Field(gt=0)


class RideResponse(BaseModel):
    ride_id: int
    source: str
    destination: str
    route: str | None
    travel_date: date
    travel_time: time
    available_seats: int
    status: RideStatus
    vehicle_id: int
    driver_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # from_attributes=True tells Pydantic that it can read values from the SQLAlchemy object's attributes


class RideUpdate(BaseModel):
    source: str | None = None
    destination: str | None = None
    route: str | None = None
    travel_date: date | None = None
    travel_time: time | None = None
    available_seats: int | None = None
    vehicle_id: int | None = None


class RideSearchRequest(BaseModel):
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    travel_date: date
    travel_time: time | None = None
    seat_required: int = Field(..., gt=0)



class RideSearchResponse(BaseModel):
    ride_id: int
    source: str
    destination: str
    travel_date: date
    travel_time: time
    available_seats: int
    status: RideStatus

    driver_id: int
    driver_name: str
    driver_profile_pic: str | None

    vehicle_id: int
    vehicle_type: str
    vehicle_brand: str
    vehicle_model: str
    vehicle_color: str


class RideDriverResponse(BaseModel):
    id: int
    full_name: str
    profile_pic: str | None = None


class RideVehicleResponse(BaseModel):
    id: int
    vehicle_type: str
    brand: str
    model: str
    year: int
    color: str
    registration_number: str
    seating_capacity: int


class RidePassengerResponse(BaseModel):
    id: int
    full_name: str
    profile_pic: str | None = None
    seats_requested: int



class RideDetailsResponse(BaseModel):
    ride_id: int

    source: str
    destination: str
    route: str | None = None

    travel_date: date
    travel_time: time

    available_seats: int
    status: RideStatus

    driver: RideDriverResponse
    vehicle: RideVehicleResponse

    passengers: list[RidePassengerResponse] = []


class RideRequestCreate(BaseModel):
    ride_id: int = Field(..., gt=0)
    seats_requested: int = Field(..., gt=0)


class RideRequestResponse(BaseModel):
    ride_request_id: int
    ride_id: int
    passenger_id: int
    passenger_name: str | None = None
    passenger_profile_pic: str | None = None
    seats_requested: int
    status: str
    created_at: datetime

    # Associated Ride Information
    source: str | None = None
    destination: str | None = None
    travel_date: date | None = None
    travel_time: time | None = None
    available_seats: int | None = None
    route: str | None = None
    ride_status: str | None = None

    # Driver Information
    driver_name: str | None = None
    driver_profile_pic: str | None = None

    model_config = ConfigDict(from_attributes=True)




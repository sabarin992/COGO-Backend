from datetime import date, time

from pydantic import BaseModel, Field, ConfigDict


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
    driver_id: int
    vehicle_id: int

    source: str
    destination: str
    route: str | None

    travel_date: date
    travel_time: time

    available_seats: int

    model_config = ConfigDict(from_attributes=True)
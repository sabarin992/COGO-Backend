from datetime import datetime, date, time

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
    source: str
    destination: str
    route: str | None
    travel_date: date
    travel_time: time
    available_seats: int
    vehicle_id: int
    driver_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    # from_attributes=True tells Pydantic that it can read values from the SQLAlchemy object's attributes



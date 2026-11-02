from datetime import datetime, date, time
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator

from app.models.recurring_ride import RecurrenceType
from app.schemas.ride import RideVehicleResponse, RideResponse


class RecurringRideCreate(BaseModel):
    vehicle_id: int
    source: str = Field(..., min_length=1)
    destination: str = Field(..., min_length=1)
    route: Optional[str] = None
    route_geometry: Optional[List[List[float]]] = None

    available_seats: int = Field(..., gt=0)
    travel_time: time

    recurrence_type: RecurrenceType
    start_date: date
    end_date: date

    # For CUSTOM
    selected_weekdays: Optional[List[int]] = None

    # For SHIFT
    working_days: Optional[int] = Field(None, gt=0)
    off_days: Optional[int] = Field(None, gt=0)
    shift_start_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_dates_and_patterns(self):
        # 1. Date range sanity
        if self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date.")

        today = date.today()
        if self.start_date < today:
            raise ValueError("Start date cannot be in the past.")

        if (self.end_date - self.start_date).days > 90:
            raise ValueError("Recurring ride range cannot exceed 90 days.")

        # 2. Shift recurrence validation
        if self.recurrence_type == RecurrenceType.SHIFT:
            if not self.working_days or self.working_days < 1:
                raise ValueError("Working days must be at least 1 for Shift Workdays recurrence.")
            if not self.off_days or self.off_days < 1:
                raise ValueError("Off days must be at least 1 for Shift Workdays recurrence.")
            if not self.shift_start_date:
                raise ValueError("Shift start date is required for Shift Workdays recurrence.")

        # 3. Custom recurrence validation
        elif self.recurrence_type == RecurrenceType.CUSTOM:
            if not self.selected_weekdays or len(self.selected_weekdays) == 0:
                raise ValueError("Please select at least one weekday for Custom recurrence.")
            for day in self.selected_weekdays:
                if day < 0 or day > 6:
                    raise ValueError(f"Invalid weekday {day}. Weekdays must be between 0 (Mon) and 6 (Sun).")

        return self


class RecurringRideUpdate(BaseModel):
    vehicle_id: Optional[int] = None
    source: Optional[str] = None
    destination: Optional[str] = None
    route: Optional[str] = None
    route_geometry: Optional[List[List[float]]] = None
    available_seats: Optional[int] = Field(None, gt=0)
    travel_time: Optional[time] = None
    end_date: Optional[date] = None
    is_active: Optional[bool] = None


class RecurringRideResponse(BaseModel):
    id: int
    driver_id: int
    vehicle_id: int
    source: str
    destination: str
    route: Optional[str] = None
    available_seats: int
    travel_time: time
    recurrence_type: str
    start_date: date
    end_date: date
    selected_weekdays: Optional[List[int]] = None
    working_days: Optional[int] = None
    off_days: Optional[int] = None
    shift_start_date: Optional[date] = None
    is_active: bool

    # Computed metrics
    total_rides: int = 0
    upcoming_rides: int = 0
    booked_rides_count: int = 0
    schedule_status: str = "Active"  # "Active", "Paused", "Completed"

    created_at: datetime
    updated_at: datetime

    vehicle: Optional[RideVehicleResponse] = None

    model_config = ConfigDict(from_attributes=True)


class GeneratedRideItem(BaseModel):
    ride_id: int
    travel_date: date
    travel_time: time
    available_seats: int
    status: str
    has_bookings: bool = False
    accepted_bookings_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class RecurringRideDetailsResponse(RecurringRideResponse):
    rides: List[GeneratedRideItem] = []

    model_config = ConfigDict(from_attributes=True)

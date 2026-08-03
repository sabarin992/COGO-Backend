from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict


class VehicleBase(BaseModel):
    vehicle_type: str
    brand: str
    model: str
    year: int
    color: str
    registration_number: str
    seating_capacity: int


class VehicleResponse(VehicleBase):
    id: int
    user_id: int
    images: List[str] | None = None
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
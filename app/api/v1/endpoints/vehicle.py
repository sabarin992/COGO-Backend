from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleResponse
from app.services.vehicle_service import create_vehicle_service

router = APIRouter()


@router.post(
    "/",
    response_model=VehicleResponse,
    status_code=201
)
def create_vehicle(
    vehicle_type: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    color: str = Form(...),
    registration_number: str = Form(...),
    seating_capacity: int = Form(...),

    images: list[UploadFile] = File(...),

    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    vehicle = create_vehicle_service(
    db=db,
    user_id=current_user.id,
    vehicle_type=vehicle_type,
    brand=brand,
    model=model,
    year=year,
    color=color,
    registration_number=registration_number,
    seating_capacity=seating_capacity,
    images=images,
)

    return vehicle
from typing import List, Optional
from fastapi import APIRouter, Depends, Form, File, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.deps import get_db
from app.schemas.vehicle import VehicleResponse
from app.services.vehicle_service import (
    create_vehicle_service,
    get_user_vehicles_service,
    get_vehicle_by_id_service,
    update_vehicle_service,
    delete_vehicle_service,
)

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
    images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return create_vehicle_service(
        db=db,
        email=email,
        vehicle_type=vehicle_type,
        brand=brand,
        model=model,
        year=year,
        color=color,
        registration_number=registration_number,
        seating_capacity=seating_capacity,
        images=images,
    )


@router.get(
    "/",
    response_model=List[VehicleResponse]
)
def get_vehicles(
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return get_user_vehicles_service(db=db, email=email)


@router.get(
    "/{vehicle_id}",
    response_model=VehicleResponse
)
def get_vehicle_by_id(
    vehicle_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return get_vehicle_by_id_service(db=db, email=email, vehicle_id=vehicle_id)


@router.put(
    "/{vehicle_id}",
    response_model=VehicleResponse
)
def update_vehicle(
    vehicle_id: int,
    vehicle_type: str = Form(...),
    brand: str = Form(...),
    model: str = Form(...),
    year: int = Form(...),
    color: str = Form(...),
    registration_number: str = Form(...),
    seating_capacity: int = Form(...),
    images: Optional[List[UploadFile]] = File(default=None),
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    return update_vehicle_service(
        db=db,
        email=email,
        vehicle_id=vehicle_id,
        vehicle_type=vehicle_type,
        brand=brand,
        model=model,
        year=year,
        color=color,
        registration_number=registration_number,
        seating_capacity=seating_capacity,
        images=images,
    )


@router.delete(
    "/{vehicle_id}"
)
def delete_vehicle(
    vehicle_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_current_user),
):
    delete_vehicle_service(db=db, email=email, vehicle_id=vehicle_id)
    return {"success": True, "message": "Vehicle deleted successfully"}
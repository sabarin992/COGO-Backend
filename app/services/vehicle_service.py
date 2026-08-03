from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.repositories import vehicle_repo, user_repo
from app.utils.cloudinary import upload_multiple_images
from app.core.exceptions import BadRequestException, NotFoundException, ForbiddenException


def create_vehicle_service(
    db: Session,
    email: str,
    vehicle_type: str,
    brand: str,
    model: str,
    year: int,
    color: str,
    registration_number: str,
    seating_capacity: int,
    images: list[UploadFile],
) -> Vehicle:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing_vehicle = vehicle_repo.get_vehicle_by_registration_number(
        db, registration_number
    )
    if existing_vehicle:
        raise BadRequestException(
            "Vehicle with this registration number already exists."
        )

    image_urls = upload_multiple_images(images) if images else []

    vehicle = Vehicle(
        user_id=user.id,
        vehicle_type=vehicle_type,
        brand=brand,
        model=model,
        year=year,
        color=color,
        registration_number=registration_number,
        seating_capacity=seating_capacity,
        images=image_urls,
    )

    return vehicle_repo.create_vehicle(db, vehicle)


def get_user_vehicles_service(db: Session, email: str) -> list[Vehicle]:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return vehicle_repo.get_vehicles_by_user_id(db, user.id)


def get_vehicle_by_id_service(db: Session, email: str, vehicle_id: int) -> Vehicle:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    vehicle = vehicle_repo.get_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise NotFoundException("Vehicle not found")

    if vehicle.user_id != user.id:
        raise ForbiddenException("Not authorized to access this vehicle")

    return vehicle


def update_vehicle_service(
    db: Session,
    email: str,
    vehicle_id: int,
    vehicle_type: str,
    brand: str,
    model: str,
    year: int,
    color: str,
    registration_number: str,
    seating_capacity: int,
    images: list[UploadFile] | None = None,
) -> Vehicle:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    vehicle = vehicle_repo.get_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise NotFoundException("Vehicle not found")

    if vehicle.user_id != user.id:
        raise ForbiddenException("Not authorized to update this vehicle")

    # Check registration number uniqueness if updated
    if registration_number != vehicle.registration_number:
        existing_vehicle = vehicle_repo.get_vehicle_by_registration_number(
            db, registration_number
        )
        if existing_vehicle:
            raise BadRequestException(
                "Vehicle with this registration number already exists."
            )

    update_data = {
        "vehicle_type": vehicle_type,
        "brand": brand,
        "model": model,
        "year": year,
        "color": color,
        "registration_number": registration_number,
        "seating_capacity": seating_capacity,
    }

    # Upload new images if provided
    if images and len(images) > 0:
        new_image_urls = upload_multiple_images(images)
        if new_image_urls:
            update_data["images"] = new_image_urls

    return vehicle_repo.update_vehicle(db, vehicle, update_data)


def delete_vehicle_service(db: Session, email: str, vehicle_id: int) -> None:
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    vehicle = vehicle_repo.get_vehicle_by_id(db, vehicle_id)
    if not vehicle:
        raise NotFoundException("Vehicle not found")

    if vehicle.user_id != user.id:
        raise ForbiddenException("Not authorized to delete this vehicle")

    vehicle_repo.delete_vehicle(db, vehicle)
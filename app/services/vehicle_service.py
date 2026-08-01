from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle
from app.repositories.vehicle_repo import create_vehicle,get_vehicle_by_registration_number
from app.utils.cloudinary import upload_multiple_images
from app.core.exceptions import BadRequestException



def create_vehicle_service(
    db: Session,
    user_id: int,
    vehicle_type: str,
    brand: str,
    model: str,
    year: int,
    color: str,
    registration_number: str,
    seating_capacity: int,
    images: list[UploadFile],
) -> Vehicle:

    existing_vehicle = get_vehicle_by_registration_number(
                        db,
                        registration_number
                    )

    if existing_vehicle:
        raise BadRequestException(
            "Vehicle with this registration number already exists."
        )

    # Upload images to Cloudinary
    image_urls = upload_multiple_images(images)

    # Create Vehicle object
    vehicle = Vehicle(
        user_id=user_id,
        vehicle_type=vehicle_type,
        brand=brand,
        model=model,
        year=year,
        color=color,
        registration_number=registration_number,
        seating_capacity=seating_capacity,
        images=image_urls,
    )

    # Save to database
    return create_vehicle(db, vehicle)
from sqlalchemy.orm import Session
from app.models.vehicle import Vehicle


def create_vehicle(db: Session, vehicle: Vehicle) -> Vehicle:
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def get_vehicle_by_registration_number(
    db: Session,
    registration_number: str
) -> Vehicle | None:
    return (
        db.query(Vehicle)
        .filter(Vehicle.registration_number == registration_number)
        .first()
    )


def get_vehicles_by_user_id(db: Session, user_id: int) -> list[Vehicle]:
    return (
        db.query(Vehicle)
        .filter(Vehicle.user_id == user_id)
        .order_by(Vehicle.created_at.desc())
        .all()
    )


def get_vehicle_by_id(db: Session, vehicle_id: int) -> Vehicle | None:
    return db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()


def update_vehicle(db: Session, vehicle: Vehicle, update_data: dict) -> Vehicle:
    for key, value in update_data.items():
        if hasattr(vehicle, key) and value is not None:
            setattr(vehicle, key, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def delete_vehicle(db: Session, vehicle: Vehicle) -> None:
    db.delete(vehicle)
    db.commit()
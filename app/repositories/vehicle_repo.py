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
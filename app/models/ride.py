from datetime import datetime,timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
)

from sqlalchemy.orm import relationship

from app.db.base import Base

class Ride(Base):
    __tablename__ = "rides"

    ride_id = Column(Integer, primary_key=True, index=True)

    driver_id = Column(
            Integer,
            ForeignKey("users.id"),
            nullable=False
        )

    vehicle_id = Column(
            Integer,
            ForeignKey("vehicles.id"),
            nullable=False
        )

    source = Column(String(150), nullable=False)

    destination = Column(String(150), nullable=False)

    route = Column(Text)

    travel_date = Column(Date, nullable=False)

    travel_time = Column(Time, nullable=False)

    available_seats = Column(Integer, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    driver = relationship("User", back_populates="rides")
    vehicle = relationship("Vehicle", back_populates="rides")
    ride_requests = relationship(
    "RideRequest",
    back_populates="ride",
    cascade="all, delete-orphan"
)
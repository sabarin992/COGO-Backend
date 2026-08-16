from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    String,
)

from sqlalchemy.orm import relationship

from app.db.base import Base


class RideRequest(Base):
    __tablename__ = "ride_requests"

    ride_request_id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ride_id = Column(
        Integer,
        ForeignKey("rides.ride_id", ondelete="CASCADE"),
        nullable=False
    )

    passenger_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    seats_requested = Column(
        Integer,
        nullable=False
    )

    status = Column(
        String(20),
        default="pending",
        nullable=False
    )

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

    ride = relationship(
    "Ride",
    back_populates="ride_requests"
    )

    passenger = relationship(
        "User",
        back_populates="ride_requests"
    )
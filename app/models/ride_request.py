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

    cancellation_reason = Column(
        String,
        nullable=True
    )

    cancelled_by_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )

    cancelled_at = Column(
        DateTime(timezone=True),
        nullable=True
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
        foreign_keys=[passenger_id],
        back_populates="ride_requests"
    )

    cancelled_by = relationship(
        "User",
        foreign_keys=[cancelled_by_id]
    )
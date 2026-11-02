import enum
from datetime import datetime, timezone
from sqlalchemy import JSON

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)

from sqlalchemy.orm import relationship

from app.db.base import Base


class RideStatus(str, enum.Enum):
    CREATED = "CREATED"
    UPCOMING = "UPCOMING"
    STARTED = "STARTED"
    REACHED_PICKUP = "REACHED_PICKUP"
    ONGOING = "ONGOING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Ride(Base):
    __tablename__ = "rides"
    __table_args__ = (
        UniqueConstraint("recurring_ride_id", "travel_date", name="uq_recurring_ride_date"),
    )

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

    recurring_ride_id = Column(
        Integer,
        ForeignKey("recurring_rides.id", ondelete="SET NULL"),
        nullable=True,
        index=True
    )

    source = Column(String(150), nullable=False)

    destination = Column(String(150), nullable=False)

    route = Column(Text)

    route_geometry = Column(JSON, nullable=True)

    travel_date = Column(Date, nullable=False)

    travel_time = Column(Time, nullable=False)

    available_seats = Column(Integer, nullable=False)

    status = Column(
        String(30),
        default=RideStatus.CREATED.value,
        nullable=False
    )

    cancellation_reason = Column(
        Text,
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

    # relationships
    driver = relationship(
        "User", 
        foreign_keys=[driver_id],
        back_populates="rides"
    )

    cancelled_by = relationship(
        "User",
        foreign_keys=[cancelled_by_id]
    )
    
    vehicle = relationship(
        "Vehicle", 
        back_populates="rides"
    )

    recurring_ride = relationship(
        "RecurringRide",
        back_populates="rides"
    )

    ride_requests = relationship(
        "RideRequest",
        back_populates="ride",
        cascade="all, delete-orphan"
    )

    chat_conversations = relationship(
        "ChatConversation",
        back_populates="ride"
    )
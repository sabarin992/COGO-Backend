import enum
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    Date,
    Time,
    DateTime,
    Boolean,
    ForeignKey,
    JSON,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class RecurrenceType(str, enum.Enum):
    ONCE = "ONCE"
    DAILY = "DAILY"
    WEEKDAYS = "WEEKDAYS"
    SHIFT = "SHIFT"
    CUSTOM = "CUSTOM"


class RecurringRide(Base):
    __tablename__ = "recurring_rides"

    id = Column(Integer, primary_key=True, index=True)

    driver_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles.id", ondelete="CASCADE"),
        nullable=False
    )

    source = Column(String(150), nullable=False)
    destination = Column(String(150), nullable=False)
    route = Column(Text, nullable=True)
    route_geometry = Column(JSON, nullable=True)

    available_seats = Column(Integer, nullable=False)
    travel_time = Column(Time, nullable=False)

    recurrence_type = Column(
        String(30),
        default=RecurrenceType.DAILY.value,
        nullable=False
    )

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    # For CUSTOM recurrence: list of weekday integers [0, 1, 2...] (0=Monday, 6=Sunday)
    selected_weekdays = Column(JSON, nullable=True)

    # For SHIFT recurrence:
    working_days = Column(Integer, nullable=True)
    off_days = Column(Integer, nullable=True)
    shift_start_date = Column(Date, nullable=True)

    is_active = Column(Boolean, default=True, nullable=False)

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

    # Relationships
    driver = relationship("User", back_populates="recurring_rides")
    vehicle = relationship("Vehicle", back_populates="recurring_rides")
    rides = relationship(
        "Ride",
        back_populates="recurring_ride",
        cascade="all, delete-orphan"
    )

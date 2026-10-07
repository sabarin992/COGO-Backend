from sqlalchemy import (
    Column,
    Integer,
    ForeignKey,
    DateTime,
    UniqueConstraint
    )
from app.db.base import Base
from datetime import datetime,timezone
from sqlalchemy.orm import relationship


class ChatConversation(Base):

    __tablename__ = "chat_conversations"

    # for each conversation should be unique
    __table_args__ = (
        UniqueConstraint(
            "ride_id",
            "driver_id",
            "passenger_id",
            name="uq_chat_conversation"
        ),
    )

    id = Column(Integer,primary_key=True,index=True)
    ride_id = Column(Integer,ForeignKey("rides.ride_id"),nullable=False)
    driver_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    passenger_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)
    updated_at = Column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),onupdate= lambda : datetime.now(timezone.utc),nullable=False)

    # relationships

    '''
    "A ChatConversation can access all its ChatMessages through messages."
    '''
    messages = relationship(
        "ChatMessage",
        back_populates="conversation"
    )

    ride = relationship(
        "Ride",
        back_populates="chat_conversations"
    )

    # When I access 'conversation.driver', use driver_id to find the User.
    driver = relationship(
        "User",
        foreign_keys=[driver_id],
        back_populates="driver_conversations"
    )

    # When I access conversation.passenger, use passenger_id to find the User
    passenger = relationship(
        "User",
        foreign_keys=[passenger_id], # For this particular relationship, use this particular foreign key.
        back_populates="passenger_conversations"
    )



    '''
    Ride
  │
  │ 1 : Many
  ▼
ChatConversation
  │
  ├── 1 : Many ──→ ChatMessage
  │
  ├── 1 : 1 ─────→ Driver (User)
  │
  └── 1 : 1 ─────→ Passenger (User)
    '''
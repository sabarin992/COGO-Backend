from sqlalchemy import Column,Integer,String,Boolean,DateTime
from datetime import datetime,timezone
from app.db.base import Base
from sqlalchemy.orm import relationship
from app.models.chat_message import ChatMessage
from app.models.chat_conversation import ChatConversation

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=True)
    
    phone = Column(String, unique=True, nullable=True)

    password = Column(String, nullable=True) 

    role = Column(String, default="consumer")
    
    profile_pic = Column(String, nullable=True)
    profile_pic_public_id = Column(String, nullable=True)

    email_verified = Column(Boolean, default=False)
 
    is_blocked = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    kyc = relationship(
        "KYC",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    vehicles = relationship(
    "Vehicle",
    back_populates="user",
    cascade="all, delete-orphan"
)

    rides = relationship(
        "Ride",
        back_populates="driver",
        cascade="all, delete-orphan"
    )

    ride_requests = relationship(
    "RideRequest",
    back_populates="passenger",
    cascade="all, delete-orphan"
)

    # to get driver conversations
    driver_conversations = relationship(
        "ChatConversation",
        foreign_keys="ChatConversation.driver_id",
        back_populates="driver"
    )

    # to get passenger conversations
    passenger_conversations = relationship(
        "ChatConversation",
        foreign_keys="ChatConversation.passenger_id",
        back_populates="passenger"
    )

    # to gets all messages sent by the user
    sent_messages = relationship(
    "ChatMessage",
    back_populates="sender"
)

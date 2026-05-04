from sqlalchemy import Column,Integer,String,Boolean,DateTime
from datetime import datetime,timezone
from app.db.base import Base
# from sqlalchemy.orm import relationship

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

    # Relationships
    # kyc_documents = relationship("KYCDocument", back_populates="user")
    # vehicles = relationship("Vehicle", back_populates="owner")

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Enum,
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.db.base import Base


class KYCStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


class KYC(Base):
    __tablename__ = "kyc"

    kyc_id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )

    document_type = Column(String(50), nullable=False)
    document_number = Column(String(100), nullable=False)

    # Front document
    front_document_url = Column(String, nullable=False)
    front_document_public_id = Column(String, nullable=False)

    # Back document (optional)
    back_document_url = Column(String, nullable=True)
    back_document_public_id = Column(String, nullable=True)

    is_verified = Column(
        Boolean,
        default=False,
        nullable=False
    )

    status = Column(
        Enum(KYCStatus),
        default=KYCStatus.PENDING,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User", back_populates="kyc")


# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     Boolean,
#     ForeignKey,
#     DateTime,
#     Enum,
# )
# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship
# import enum
# from app.db.base import Base


# class KYCStatus(str, enum.Enum):
#     PENDING = "pending"
#     VERIFIED = "verified"
#     REJECTED = "rejected"


# class KYC(Base):
#     __tablename__ = "kyc"

#     kyc_id = Column(Integer, primary_key=True, index=True)

#     user_id = Column(
#     Integer,
#     ForeignKey("users.id", ondelete="CASCADE"),
#     nullable=False,
#     unique=True
# )

#     document_type = Column(String(50), nullable=False)
#     document_number = Column(String(100), nullable=False)

#     is_verified = Column(
#         Boolean,
#         default=False,
#         nullable=False
#     )

#     status = Column(
#         Enum(KYCStatus),
#         default=KYCStatus.PENDING,
#         nullable=False
#     )

   

#     created_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now()
#     )

#     updated_at = Column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         onupdate=func.now()
#     )

#     user = relationship("User", back_populates="kyc")
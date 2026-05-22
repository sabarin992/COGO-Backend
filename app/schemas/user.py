from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class EditProfile(BaseModel):
    full_name: str
    phone: str | None = None


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str | None
    phone: str | None
    role: str
    email_verified: bool
    is_blocked: bool
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedUserResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
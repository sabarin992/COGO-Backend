from pydantic import BaseModel, EmailStr, Field

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)

class EditProfile(BaseModel):
    full_name: str
    phone: str | None = None
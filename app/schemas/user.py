from pydantic import BaseModel, EmailStr, Field

class ResetPasswordRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
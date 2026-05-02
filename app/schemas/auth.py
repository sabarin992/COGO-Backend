from pydantic import BaseModel,EmailStr, Field, field_validator
import re

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    password: str = Field(..., min_length=6)

    # phone number validation like country code + 10 digit phone number
    @field_validator("phone")
    def validate_phone(cls, v):
        # E.164 format (international)
        pattern = r"^\+\d{10,15}$"
        if not re.match(pattern, v):
            raise ValueError("Phone must be in international format (+countrycode...)")
        return v

    # password validation for strong password
    @field_validator("password")
    def validate_password(cls, v):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).+$"
        if not re.match(pattern, v):
            raise ValueError(
                "Password must contain uppercase, lowercase, number and special character"
            )
        return v
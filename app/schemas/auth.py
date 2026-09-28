from pydantic import BaseModel,EmailStr, Field, field_validator
import re

class LoginRequest(BaseModel):
    email:EmailStr
    password:str

class RegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=12, max_length=14)
    password: str = Field(..., min_length=8)

    # Full name validation: alphabets and spaces only, 3-50 chars after trimming
    @field_validator("full_name")
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Minimum 3 characters required")
        if len(v) > 50:
            raise ValueError("Maximum 50 characters allowed")
        if not re.match(r"^[A-Za-z\s]+$", v):
            raise ValueError("Only alphabets and spaces allowed")
        return v

    # Phone number validation: country code (+) + 1-3 digits country code + 10 digits
    @field_validator("phone")
    def validate_phone(cls, v: str) -> str:
        pattern = r"^\+\d{1,3}\d{10}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Must include country code (+) and exactly 10 digits (e.g. +919876543210)"
            )
        return v

    # Password validation: min 8 chars, 1 uppercase, 1 lowercase, 1 number, 1 special char
    @field_validator("password")
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Minimum 8 characters required")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Must contain one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Must contain one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Must contain one number")
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Must contain one special character")
        return v
    

class GoogleToken(BaseModel):
    token: str
from pydantic import BaseModel, EmailStr

class OTPBase(BaseModel):
    email: EmailStr

class OTPSendRequest(OTPBase):
    pass

class OTPVerifyRequest(OTPBase):
    otp: str
from fastapi import APIRouter,Depends
from app.schemas.otp import OTPVerifyRequest
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services import otp_service


router = APIRouter()

@router.post("/verify-otp")
def verify_otp(data:OTPVerifyRequest, db: Session = Depends(get_db)):
    print(data)
    return otp_service.verify_otp(db, data.email, data.otp)
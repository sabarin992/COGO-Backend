from fastapi import APIRouter,Depends,HTTPException
from app.schemas.otp import OTPVerifyRequest,OTPSendRequest
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services import otp_service


router = APIRouter()

@router.post("/send-otp")
def send_otp(data: OTPSendRequest):
    try:
        otp_service.send_otp(data.email)

        return {
            "message": "OTP sent successfully"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to send OTP"
        )

@router.post("/verify-otp")
def verify_otp(data:OTPVerifyRequest, db: Session = Depends(get_db)):
    return otp_service.verify_otp(db, data.email, data.otp)
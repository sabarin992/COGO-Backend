from fastapi import APIRouter,Depends,HTTPException
from app.schemas.otp import OTPVerifyRequest,OTPSendRequest,OTPResendRequest
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.services import otp_service


router = APIRouter()

@router.post("/send-otp")
def send_otp(data: OTPSendRequest,db: Session = Depends(get_db)):
    try:
        otp_service.send_otp(db,data.email)

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

@router.post("/resend-otp")
def resend_otp(data: OTPResendRequest):
    try:
        otp_service.resend_otp(data.email)

        return {
            "message": "OTP resent successfully"
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to resend OTP"
        )
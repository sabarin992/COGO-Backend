import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.redis import redis_client
from app.repositories import user_repo
from app.utils.email import send_otp_email
from app.utils.otp import generate_otp
from app.core.config import settings

def verify_otp(db: Session, email: str, otp: str):
    stored_data = redis_client.get(f"otp:{email}")

    if not stored_data:
        raise HTTPException(status_code=400, detail="OTP expired or not found")

    data = json.loads(stored_data)

    if data["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    try:
        user = user_repo.get_user_by_email(db, email)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # verify user
        user_repo.verify_user_by_email(db,user)

        # delete OTP after success
        redis_client.delete(f"otp:{email}")

        return {"message": "User verified successfully"}

    except HTTPException:
        raise

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")
    

def send_otp(email: str):
    try:
        # prevent spam
        if redis_client.exists(f"otp:{email}"):
            raise HTTPException(
                status_code=400,
                detail="OTP already sent. Try again later"
            )

        # generate OTP
        otp = generate_otp()

        # store in Redis
        redis_client.setex(
            f"otp:{email}",
            settings.OTP_EXPIRE_SECONDS,
            json.dumps({
            "otp": otp,
        })
        )

        # send the otp to email
        send_otp_email(email, otp)

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )
    

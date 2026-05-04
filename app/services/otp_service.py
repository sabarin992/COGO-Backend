import json
from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.core.redis import redis_client
from app.repositories import user_repo

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
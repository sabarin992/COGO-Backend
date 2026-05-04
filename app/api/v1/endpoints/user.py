from fastapi import APIRouter,Request,Depends
from app.api.deps import get_current_user
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.schemas.user import ResetPasswordRequest
from app.services import user_service


router = APIRouter()


@router.get("/profile")
def profile(request:Request,user=Depends(get_current_user)):
    return {"user_email":user}


@router.get("/check-auth")
def check_auth(user=Depends(get_current_user)):
    return user


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    
    user_service.reset_password(data,db)
    return {"message": "Password updated successfully"}
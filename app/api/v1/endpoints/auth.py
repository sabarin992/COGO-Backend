from fastapi import APIRouter,HTTPException,Response,Depends
from app.schemas.auth import LoginRequest,RegisterRequest
from app.core.security import create_access_token
from app.api.deps import get_current_user
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.services import auth_service


router = APIRouter()


@router.post("/login")
def login(data:LoginRequest,response:Response,db:Session = Depends(get_db)):
    user = auth_service.login_user(db, data,response)
    return {
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email
    }



@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, data)
    return {
        "message": "User created successfully",
        "user_id": user.id,
        "email": user.email
    }


@router.post("/logout")
def logout(response:Response,user=Depends(get_current_user)):
    response.delete_cookie("access_token")
    return {"message":"Logout Successful"}
    
from fastapi import APIRouter,HTTPException,Response,Depends
from app.schemas.auth import LoginRequest,RegisterRequest,GoogleToken
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



from fastapi import APIRouter, HTTPException
from app.schemas.auth import GoogleToken
from app.services.google_auth import verify_google_token
from app.core.security import create_access_token
from app.services import google_auth



# Fake DB (replace with real DB)
fake_db = []

# API for google login
@router.post("/google")
def google_login(data: GoogleToken, response: Response, db: Session = Depends(get_db)):
    
    result = google_auth.google_login(data, db)

    # 🍪 Set access token cookie
    response.set_cookie(
        key="access_token",
        value=result["access_token"],
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=900
    )

    # # 🍪 Set refresh token cookie
    # response.set_cookie(
    #     key="refresh_token",
    #     value=result["refresh_token"],
    #     httponly=True,
    #     secure=False,
    #     samesite="Lax",
    #     max_age=60 * 60 * 24 * 7,
    #     domain="localhost"
    # )

    return {
        "message": "Google login successful",
        "user": result["user"]
    }



@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    user = auth_service.register_user(db, data)
    return user
    # return {
    #     "message": "User created successfully",
    #     "user_id": user.id,
    #     "email": user.email
    # }


@router.post("/logout")
def logout(response:Response,user=Depends(get_current_user)):
    response.delete_cookie("access_token")
    return {"message":"Logout Successful"}



    
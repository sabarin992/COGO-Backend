from fastapi import APIRouter,HTTPException,Response,Depends,Request
from app.schemas.auth import LoginRequest,RegisterRequest,GoogleToken
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.api.deps import get_current_user
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.services import auth_service
from app.services.google_auth import verify_google_token
from app.services import google_auth
from app.repositories import user_repo
from datetime import datetime,timedelta,timezone
from app.core.token_blacklist import blacklist_token,is_token_blacklisted




router = APIRouter()


@router.post("/login")
def login(data:LoginRequest,response:Response,db:Session = Depends(get_db)):
    user = auth_service.login_user(db, data,response)
    return {
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email
    }


@router.post("/admin/login")
def admin_login(data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = auth_service.login_admin(db, data, response)
    return {
        "message": "Admin login successful",
        "user_id": user.id,
        "email": user.email
    }







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

    # 🍪 Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=604800
    )

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


# @router.post("/logout")
# def logout(response:Response):
#     response.delete_cookie("access_token")
#     response.delete_cookie("refresh_token")
#     return {"message":"Logout Successful"}



@router.post("/logout")
def logout(
    request: Request,
    response: Response
):

    refresh_token = request.cookies.get("refresh_token")

    if refresh_token:

        payload = verify_token(refresh_token)

        if payload:

            jti = payload.get("jti")

            exp = payload.get("exp")

            if jti and exp:

                current_time = datetime.now(
                    timezone.utc
                ).timestamp()

                expires_in = int(exp - current_time)

                blacklist_token(
                    jti,
                    expires_in
                )

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")

    return {
        "message": "Logout successful"
    }


# @router.post("/refresh")
# def refresh(request: Request, response: Response, db: Session = Depends(get_db)):
#     refresh_token_val = request.cookies.get("refresh_token")
#     if not refresh_token_val:
#         raise HTTPException(status_code=401, detail="Refresh token missing")
    
#     payload = verify_token(refresh_token_val)
#     if payload is None:
#         raise HTTPException(status_code=401, detail="Invalid refresh token")
    
#     if payload.get("token_type") != "refresh":
#         raise HTTPException(status_code=401, detail="Invalid token type")
        
#     email = payload.get("sub")
#     if not email:
#         raise HTTPException(status_code=401, detail="Invalid token payload")
        
#     user = user_repo.get_user_by_email(db, email)
#     if not user:
#         raise HTTPException(status_code=401, detail="User not found")
        
#     if user.is_blocked:
#         raise HTTPException(status_code=403, detail="User is blocked")
        
#     # Generate new access and refresh tokens (rotation)
#     new_access_token = create_access_token({"sub": email})
#     new_refresh_token = create_refresh_token({"sub": email})
    
#     # Set cookies
#     response.set_cookie(
#         key="access_token",
#         value=new_access_token,
#         httponly=True,
#         samesite="lax",
#         secure=False,
#         max_age=900
#     )
    
#     response.set_cookie(
#         key="refresh_token",
#         value=new_refresh_token,
#         httponly=True,
#         samesite="lax",
#         secure=False,
#         max_age=604800 # 7 days
#     )
    
#     return {"message": "Token refreshed successfully"}




@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):

    refresh_token_val = request.cookies.get(
        "refresh_token"
    )

    if not refresh_token_val:
        raise HTTPException(
            status_code=401,
            detail="Refresh token missing"
        )

    payload = verify_token(refresh_token_val)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token"
        )

    jti = payload.get("jti")

    # CHECK BLACKLIST
    if is_token_blacklisted(jti):

        raise HTTPException(
            status_code=401,
            detail="Refresh token blacklisted"
        )

    email = payload.get("sub")

    user = user_repo.get_user_by_email(
        db,
        email
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )

    # ROTATE TOKENS
    new_access_token = create_access_token({
        "sub": email
    })

    new_refresh_token = create_refresh_token({
        "sub": email
    })

    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=900
    )

    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=604800
    )

    return {
        "message": "Token refreshed successfully"
    }



    
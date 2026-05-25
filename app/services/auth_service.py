from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.core.security import hash_password,verify_password,create_access_token,create_refresh_token
from fastapi import HTTPException,Response
from sqlalchemy.exc import IntegrityError
from app.schemas.auth import LoginRequest
from app.core.redis import redis_client
from app.utils.otp import generate_otp
from app.utils.email import send_otp_email
import json


OTP_EXPIRE_SECONDS = 60 # otp will expire after 1 minute

def register_user(db: Session, data):

    # check user exists by using email
    existing_user = user_repo.get_user_by_email(db, data.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    # check user exists by using phone number
    existing_user = user_repo.get_user_by_phone(db, data.phone)
    if existing_user:
        raise HTTPException(status_code=400, detail="Phone number already exists")

    user_data = data.model_dump() # convert pydantic to dictinary
    hashed = hash_password(user_data["password"])  # hash password
    user_data["password"] = hashed  # update the password to hashed password 

    # generate OTP
    otp = generate_otp()

    # store user data + otp in redis
    redis_client.setex(
        f"otp:{data.email}",
        OTP_EXPIRE_SECONDS,
        json.dumps({
            "otp": otp,
            "user_data": user_data
        })
    )

    try:
        user = user_repo.create_user(db, user_data) # create user 
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")

    # send OTP to email
    send_otp_email(data.email, otp)

    return {"message": "OTP sent to your email"}

def login_user(db, data:LoginRequest,response:Response):

    # check user exists
    user = user_repo.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_blocked:
        raise HTTPException(status_code=403, detail="User is blocked")

    # check password
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

     # create access and refresh tokens
    token = create_access_token({"sub":data.email})
    refresh_token = create_refresh_token({"sub":data.email})

    # set the access token in the cookies
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=900
    )

    # set the refresh token in the cookies
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=604800 # 7 days
    )

    return user


def login_admin(db: Session, data: LoginRequest, response: Response):
    # Retrieve user from database via repository
    user = user_repo.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.is_blocked:
        raise HTTPException(status_code=403, detail="User is blocked")

    # Check if the user has the required admin privileges
    if user.role != "admin":
        raise HTTPException(
            status_code=403, 
            detail="Access denied. Admin access only."
        )

    # Verify matching hashed password credentials
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create administrative session access and refresh tokens
    token = create_access_token({"sub": data.email})
    refresh_token = create_refresh_token({"sub": data.email})

    # Set security authorization cookie
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=900
    )

    # Set refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=604800 # 7 days
    )

    return user
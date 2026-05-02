from sqlalchemy.orm import Session
from app.repositories import user_repo
from app.core.security import hash_password,verify_password,create_access_token
from fastapi import HTTPException,Response
from sqlalchemy.exc import IntegrityError
from app.schemas.auth import LoginRequest



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

    try:
        user = user_repo.create_user(db, user_data) # create user 
        return user

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User already exists")

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong")



def login_user(db, data:LoginRequest,response:Response):

    # check user exists
    user = user_repo.get_user_by_email(db, data.email)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # check password
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

     # create access token
    token = create_access_token({"sub":data.email})

    # set the access token in the cookies
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=900
    )

    return user
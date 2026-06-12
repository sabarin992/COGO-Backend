from fastapi import HTTPException
from app.core.security import hash_password, create_access_token, create_refresh_token
from app.repositories import user_repo
from app.core.exceptions import UserNotFoundError
from sqlalchemy.exc import IntegrityError
import phonenumbers
import json
from app.core.redis import redis_client
from app.core.config import settings
from app.utils.otp import generate_otp
from app.utils.email import send_otp_email




def reset_password(data,db):
    user = user_repo.get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(404, "User not found")

    user.password = hash_password(data.password)

    db.commit()


def profile_service(db, email):
    user = user_repo.get_user_by_email(db, email)

    if not user:
        raise UserNotFoundError("User not found")

    return user


def edit_profile_service(db,email,data):

    
    # Check user exists
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate phone format
    try:
        parsed = phonenumbers.parse(data.phone, None)

        if not phonenumbers.is_valid_number(parsed):
            raise HTTPException(
                status_code=400,
                detail="Enter a valid phone number with country code."
            )

        # Normalize phone (IMPORTANT)
        phone = phonenumbers.format_number(
            parsed,
            phonenumbers.PhoneNumberFormat.E164
        )

    except phonenumbers.NumberParseException:
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Use +<countrycode><number>."
        )

    # Optional pre-check (better UX)
    existing_user = user_repo.get_user_by_phone(db, phone)

    if existing_user and existing_user.id != user.id:
        raise HTTPException(
            status_code=400,
            detail="This phone number is already in use."
        )

    # Update handle DB error
    try:
        return user_repo.edit_user_profile(
            db,
            user,
            data
        )

    except IntegrityError:
        db.rollback() 

        raise HTTPException(
            status_code=400,
            detail="This phone number is already in use."
        )


# get all users except admin
def get_users_except_admin_service(
    db, 
    search: str | None = None, 
    status: str | None = None,
    page: int = 1,
    size: int = 5
):
    users, total = user_repo.get_all_users_except_admin(db, search, status, page, size)
    return {
        "users": users,
        "total": total,
        "page": page,
        "size": size
    }


# block user
def block_user_service(db, user_id):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role == "admin":
        raise HTTPException(status_code=403, detail="Cannot block admin")
    return user_repo.update_user_block_status(db, user, True)

# unblock user
def unblock_user_service(db, user_id):
    user = user_repo.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user_repo.update_user_block_status(db, user, False)


def request_email_update_service(db, current_user_email, new_email):
    if current_user_email == new_email:
        raise HTTPException(status_code=400, detail="New email must be different from current email")

    existing_user = user_repo.get_user_by_email(db, new_email)
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already in use")

    if redis_client.exists(f"otp:{new_email}"):
        raise HTTPException(status_code=400, detail="OTP already sent. Try again later")

    otp = generate_otp()

    redis_client.setex(
        f"otp:{new_email}",
        settings.OTP_EXPIRE_SECONDS,
        json.dumps({"otp": otp})
    )

    send_otp_email(new_email, otp)


def verify_email_update_service(db, current_user_email, new_email, otp, response):
    if current_user_email == new_email:
        raise HTTPException(status_code=400, detail="New email must be different from current email")

    stored_data = redis_client.get(f"otp:{new_email}")
    if not stored_data:
        raise HTTPException(status_code=400, detail="OTP expired or not found")

    data = json.loads(stored_data)
    if data["otp"] != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    existing_user = user_repo.get_user_by_email(db, new_email)
    if existing_user:
        raise HTTPException(status_code=400, detail="This email is already in use")

    user = user_repo.get_user_by_email(db, current_user_email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.email = new_email
    db.commit()
    db.refresh(user)

    redis_client.delete(f"otp:{new_email}")

    new_access_token = create_access_token({"sub": new_email})
    new_refresh_token = create_refresh_token({"sub": new_email})

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

    return user


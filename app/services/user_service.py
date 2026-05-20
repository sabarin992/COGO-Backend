from fastapi import HTTPException
from app.core.security import hash_password
from app.repositories import user_repo
from app.core.exceptions import UserNotFoundError
from sqlalchemy.exc import IntegrityError
import phonenumbers



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
def get_users_except_admin_service(db, search: str | None = None):
    return user_repo.get_all_users_except_admin(db, search)


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

from fastapi import HTTPException
from app.core.security import hash_password
from app.repositories import user_repo
from app.core.exceptions import UserNotFoundError



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


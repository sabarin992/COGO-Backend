from fastapi import HTTPException
from app.core.security import hash_password
from app.repositories import user_repo



def reset_password(data,db):
    user = user_repo.get_user_by_email(db, data.email)

    if not user:
        raise HTTPException(404, "User not found")

    user.password = hash_password(data.password)

    db.commit()


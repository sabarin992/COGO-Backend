from app.repositories import kyc_repo,user_repo
from fastapi import HTTPException

def upload_kyc_service(db, data, email):

    # Business logic can go here
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")



    return kyc_repo.create_kyc(db, data, user)
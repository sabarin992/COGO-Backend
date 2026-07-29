from app.repositories import kyc_repo,user_repo
from fastapi import HTTPException

import cloudinary.uploader

def upload_kyc_service(db, data, email):

    user = user_repo.get_user_by_email(db, email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    front_result = cloudinary.uploader.upload(
        data["front_document"].file,
        folder="kyc/front"
    )

    back_result = None

    if data["back_document"]:
        back_result = cloudinary.uploader.upload(
            data["back_document"].file,
            folder="kyc/back"
        )

    data["front_document_url"] = front_result["secure_url"]
    data["front_document_public_id"] = front_result["public_id"]

    if back_result:
        data["back_document_url"] = back_result["secure_url"]
        data["back_document_public_id"] = back_result["public_id"]

    return kyc_repo.create_kyc(db, data, user)






def get_kyc(db,email):
    user = user_repo.get_user_by_email(db, email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    return kyc_repo.get_kyc(db,user)
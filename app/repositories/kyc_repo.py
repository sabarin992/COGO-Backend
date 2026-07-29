from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.kyc_docs import KYC


def create_kyc(db, data, user):

    existing_kyc = db.query(KYC).filter(
        KYC.user_id == user.id
    ).first()

    if existing_kyc:
        raise HTTPException(
            status_code=400,
            detail="KYC already exists."
        )

    try:
        kyc = KYC(
            user_id=user.id,
            document_type=data["document_type"],
            document_number=data["document_number"],

            front_document_url=data["front_document_url"],
            front_document_public_id=data["front_document_public_id"],

            back_document_url=data.get("back_document_url"),
            back_document_public_id=data.get("back_document_public_id"),
        )

        db.add(kyc)
        db.commit()
        db.refresh(kyc)

        return kyc

    except IntegrityError:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="KYC already exists."
        )

    except Exception:
        db.rollback()
        raise



def get_kyc(db,user):
    kyc = db.query(KYC).filter(KYC.user_id == user.id).first()
    return kyc


# from app.models.kyc_docs import KYC
# from sqlalchemy.exc import IntegrityError
# from fastapi import HTTPException


# def create_kyc(db, data, user):

#     existing_kyc = db.query(KYC).filter(KYC.user_id == user.id).first()

#     if existing_kyc:
#         raise HTTPException(
#             status_code=400,
#             detail="KYC already exists."
#         )

#     try:
#         kyc = KYC(
#             user_id=user.id,
#             document_type=data["document_type"],
#             document_number=data["document_number"]
#         )

#         db.add(kyc)
#         db.commit()
#         db.refresh(kyc)

#         return kyc

#     except IntegrityError:
#         db.rollback()
#         raise HTTPException(
#             status_code=400,
#             detail="KYC already exists."
#         )




   
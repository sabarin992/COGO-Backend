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



from app.models.user import User
from app.models.kyc_docs import KYCStatus

def get_kyc(db,user):
    kyc = db.query(KYC).filter(KYC.user_id == user.id).first()
    return kyc


def get_admin_kyc_list(db, search=None, status=None, page=1, size=10):
    query = db.query(KYC).join(User)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern)) |
            (KYC.document_number.ilike(search_pattern))
        )

    if status and status.lower() != "all":
        query = query.filter(KYC.status == status.lower())

    total = query.count()
    offset = (page - 1) * size
    items = query.order_by(KYC.created_at.desc()).offset(offset).limit(size).all()

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": (total + size - 1) // size if total > 0 else 1
    }


def approve_kyc(db, kyc_id):
    kyc = db.query(KYC).filter(KYC.kyc_id == kyc_id).first()
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC record not found")
    kyc.status = KYCStatus.VERIFIED
    kyc.is_verified = True
    kyc.rejection_reason = None
    if kyc.user:
        kyc.user.role = "rider"
    db.commit()
    db.refresh(kyc)
    return kyc


def reject_kyc(db, kyc_id, reason):
    kyc = db.query(KYC).filter(KYC.kyc_id == kyc_id).first()
    if not kyc:
        raise HTTPException(status_code=404, detail="KYC record not found")
    kyc.status = KYCStatus.REJECTED
    kyc.is_verified = False
    kyc.rejection_reason = reason
    db.commit()
    db.refresh(kyc)
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




   
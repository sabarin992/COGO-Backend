from fastapi import APIRouter, Depends, Form, File, UploadFile
from app.services import kyc_service
from app.schemas.kyc import KYCCreate, KYCResponse
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, get_current_admin
from pydantic import BaseModel

router = APIRouter()

class RejectRequest(BaseModel):
    reason: str


@router.get("/kyc-docs")
def get_kyc(db=Depends(get_db), email=Depends(get_current_user)):
    print("hello")
    v = kyc_service.get_kyc(db, email)
    print(v)
    return v


@router.post("/upload-kyc")
async def upload_kyc(
    document_type: str = Form(...),
    document_number: str = Form(...),
    front_document: UploadFile = File(...),
    back_document: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    email=Depends(get_current_user)
):
    data = {
        "document_type": document_type,
        "document_number": document_number,
        "front_document": front_document,
        "back_document": back_document
    }
    
    kyc_service.upload_kyc_service(db, data, email)
    return {"message": "KYC Uploaded Successfully"}


@router.get("/admin/kyc-list")
def get_admin_kyc_list(
    search: str | None = None,
    status: str | None = None,
    page: int = 1,
    size: int = 10,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    try:
        result = kyc_service.get_admin_kyc_list_service(db, search, status, page, size)

        formatted_items = []
        for kyc in result["items"]:
            user = kyc.user
            status_val = kyc.status.value if hasattr(kyc.status, "value") else str(kyc.status)
            rejection_reason = getattr(kyc, "rejection_reason", None)
            
            formatted_items.append({
                "kyc_id": kyc.kyc_id,
                "user_id": user.id if user else None,
                "user_name": user.full_name if user else "Unknown",
                "user_email": user.email if user else "",
                "user_code": f"USR-{user.id:05d}" if user else f"USR-{kyc.user_id}",
                "user_created_at": user.created_at.strftime("%b %d, %Y") if user and user.created_at else "N/A",
                "document_type": kyc.document_type,
                "document_number": kyc.document_number,
                "front_document_url": kyc.front_document_url,
                "back_document_url": kyc.back_document_url,
                "status": status_val,
                "rejection_reason": rejection_reason,
                "created_at": kyc.created_at.strftime("%b %d, %Y") if kyc.created_at else "N/A",
                "updated_at": kyc.updated_at.strftime("%b %d, %Y") if kyc.updated_at else "N/A"
            })

        return {
            "items": formatted_items,
            "total": result["total"],
            "page": result["page"],
            "size": result["size"],
            "pages": result["pages"]
        }
    except Exception as e:
        print("Error in get_admin_kyc_list:", e)
        return {
            "items": [],
            "total": 0,
            "page": page,
            "size": size,
            "pages": 1
        }


@router.patch("/admin/approve/{kyc_id}")
def approve_kyc(
    kyc_id: int,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    kyc = kyc_service.approve_kyc_service(db, kyc_id)
    return {"message": "KYC Approved Successfully", "status": kyc.status.value if hasattr(kyc.status, "value") else str(kyc.status)}


@router.patch("/admin/reject/{kyc_id}")
def reject_kyc(
    kyc_id: int,
    data: RejectRequest,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    kyc = kyc_service.reject_kyc_service(db, kyc_id, data.reason)
    return {"message": "KYC Rejected Successfully", "status": kyc.status.value if hasattr(kyc.status, "value") else str(kyc.status)}
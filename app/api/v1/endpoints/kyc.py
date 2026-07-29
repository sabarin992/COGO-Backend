from fastapi import APIRouter,Depends,Form, File, UploadFile
from app.services import kyc_service
from app.schemas.kyc import KYCCreate,KYCResponse
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user



router = APIRouter()



@router.get("/kyc-docs")
def get_kyc(db=Depends(get_db),email=Depends(get_current_user)):
    print("hello")
    v = kyc_service.get_kyc(db,email)
    print(v)
    return v


# @router.post("/upload-kyc", response_model=KYCResponse)
# def upload_kyc(
#     data: KYCCreate,
#     db: Session = Depends(get_db),
#     email=Depends(get_current_user)
# ):
#     return kyc_service.upload_kyc_service(db, data, email)

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
        "document_type":document_type,
        "document_number":document_number,
        "front_document":front_document,
        "back_document":back_document
        }
    
    kyc_service.upload_kyc_service(db, data, email)
    return {"message":"KYC Uploaded Successfully"}
from fastapi import APIRouter,Depends
from app.services import kyc_service
from app.schemas.kyc import KYCCreate,KYCResponse
from app.db.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user



router = APIRouter()



@router.get("/kyc-docs")
def get_kyc_docs():
    v = kyc_service.get_kyc_docs()
    return {"api_response":'This is an api for getting kyc documents',**v}


@router.post("/upload-kyc", response_model=KYCResponse)
def upload_kyc(
    data: KYCCreate,
    db: Session = Depends(get_db),
    email=Depends(get_current_user)
):
    return kyc_service.upload_kyc_service(db, data, email)
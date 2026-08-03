from pydantic import BaseModel,ConfigDict
from typing import Optional
from app.models.kyc_docs import KYCStatus
from datetime import datetime


class KYCCreate(BaseModel):
    document_type: str
    document_number: str


class KYCResponse(BaseModel):
    kyc_id: int
    user_id: int
    document_type: str
    document_number: str
    is_verified: bool
    status: KYCStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)









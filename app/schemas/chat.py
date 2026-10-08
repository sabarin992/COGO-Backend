from datetime import datetime
from pydantic import BaseModel


class ChatMessageCreate(BaseModel):
    message: str


class ChatMessageResponse(BaseModel):
    id: int
    conversation_id: int
    sender_id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
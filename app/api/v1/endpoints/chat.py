from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import EmailStr

from app.schemas.chat import (
    ChatMessageCreate,
    ChatMessageResponse
    )

from app.db.deps import get_db
from app.api.deps import get_current_user
from app.services import chat_service


router = APIRouter()


# Get messages of a conversation
@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=list[ChatMessageResponse],
)
def get_conversation_messages(
    conversation_id: int,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        email=email,
    )


@router.post(
    "/conversations/{conversation_id}/messages",
    response_model=ChatMessageResponse,
)
def send_message(
    conversation_id: int,
    message_data: ChatMessageCreate,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return chat_service.send_message(
        db=db,
        conversation_id=conversation_id,
        email=email,
        message=message_data.message,
    )
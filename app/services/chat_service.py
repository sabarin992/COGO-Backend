from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException,NotFoundException
from pydantic import EmailStr
from app.repositories import user_repo

from app.repositories.chat_repository import (
    get_conversation,
    create_conversation,
     create_message,
     get_conversation_by_id,
     get_messages
)



def get_or_create_conversation(
        db: Session,
        ride_id: int,
        driver_id: int,
        passenger_id: int
    ):

    conversation = get_conversation(db,ride_id,driver_id,passenger_id)
    if not conversation:
        conversation = create_conversation(db,ride_id,driver_id,passenger_id)

    return conversation


def send_message(
    db: Session,
    conversation_id: int,
    email : EmailStr,
    message: str
):
    conversation = get_conversation_by_id(db,conversation_id)

    if not conversation:
        raise BadRequestException(
            "Conversation not found"
        )

    sender = user_repo.get_user_by_email(db=db,email=email)

    if not sender:
        raise NotFoundException(
            "User not found"
        )
    
    if sender.id == conversation.driver_id or sender.id == conversation.passenger_id:
        chat_message = create_message(db,conversation_id,sender.id,message)
    else:
        raise BadRequestException(
                    "You are not allowed to send this message"
                )
    return chat_message


def get_conversation_messages(
    db: Session,
    conversation_id: int,
    email: EmailStr
):
    conversation = get_conversation_by_id(
        db,
        conversation_id
    )

    if not conversation:
        raise BadRequestException(
            "Conversation not found"
        )

    user = user_repo.get_user_by_email(
        db=db,
        email=email
    )

    if not user:
        raise NotFoundException(
            "User not found."
        )

    if (
        user.id == conversation.driver_id
        or user.id == conversation.passenger_id
    ):
        messages = get_messages(
            db,
            conversation_id
        )
    else:
        raise BadRequestException(
            "You are not the driver or passenger of this conversation"
        )

    return messages
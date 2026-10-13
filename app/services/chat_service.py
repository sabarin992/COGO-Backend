from sqlalchemy.orm import Session
from app.core.exceptions import BadRequestException,NotFoundException
from pydantic import EmailStr
from app.repositories import user_repo

from app.repositories.chat_repository import (
    get_conversation,
    create_conversation,
     create_message,
     get_conversation_by_id,
     get_messages,
     get_conversation_by_ride_request_id,
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


def send_message_by_user_id(
    db: Session,
    conversation_id: int,
    user_id: int,
    message: str,
):
    conversation = get_conversation_by_id(
        db,
        conversation_id
    )

    if not conversation:
        raise NotFoundException(
            "Conversation not found"
        )

    if (
        user_id != conversation.driver_id
        and user_id != conversation.passenger_id
    ):
        raise BadRequestException(
            "You are not the driver or passenger of this conversation"
        )

    chat_message = create_message(
        db=db,
        conversation_id=conversation_id,
        sender_id=user_id,
        message=message,
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

    return [
        {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "sender_id": msg.sender_id,
            "sender_name": msg.sender.full_name if msg.sender else None,
            "message": msg.message,
            "created_at": msg.created_at,
        }
        for msg in messages
    ]


def get_conversation_by_request(
    db: Session,
    ride_request_id: int,
    email: EmailStr,
):
    """
    Return the ChatConversation for the given ride_request_id.
    Only the driver or passenger of that request may call this.
    Returns None if no conversation exists yet (request not accepted).
    """
    user = user_repo.get_user_by_email(db=db, email=email)
    if not user:
        raise NotFoundException("User not found.")

    conversation = get_conversation_by_ride_request_id(
        db=db,
        ride_request_id=ride_request_id,
    )

    if not conversation:
        return None

    # Authorisation: only the driver or passenger may access
    if user.id != conversation.driver_id and user.id != conversation.passenger_id:
        raise BadRequestException(
            "You are not authorised to access this conversation."
        )

    return conversation
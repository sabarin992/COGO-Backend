from sqlalchemy.orm import Session
from app.models.chat_conversation import ChatConversation
from app.models.chat_message import ChatMessage


def get_conversation(
        db:Session,
        ride_id:int,
        driver_id:int,
        passenger_id:int
):

    conversation = db.query(ChatConversation).filter(
        ChatConversation.ride_id == ride_id,
        ChatConversation.driver_id == driver_id,
        ChatConversation.passenger_id == passenger_id
    ).first()
    
    return conversation


def create_conversation(
        db:Session,
        ride_id:int,
        driver_id:int,
        passenger_id:int
        ):
    conversation = ChatConversation(
        ride_id = ride_id,
        driver_id = driver_id,
        passenger_id = passenger_id
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    return conversation


def create_message(
        db:Session,
        conversation_id:int,
        sender_id:int,
        message:str
):

    chat_message = ChatMessage(
        conversation_id=conversation_id,
        sender_id=sender_id,
        message=message
    )

    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message


def get_messages(
        db:Session,
        conversation_id:int
):
    messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at).all()

    return messages

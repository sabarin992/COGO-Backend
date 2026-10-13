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


from fastapi import (
    APIRouter,
    Depends,
    WebSocket,
    WebSocketDisconnect,
    HTTPException,
)

from sqlalchemy.orm import Session

from app.db.deps import get_db
from app.api.deps import get_current_user_ws
from app.repositories.chat_repository import get_conversation_by_id
from app.websocket.connection_manager import ConnectionManager


router = APIRouter()

manager = ConnectionManager()


@router.websocket("/ws/chat/{conversation_id}")
async def chat_websocket(
    websocket: WebSocket,
    conversation_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user_ws),
):
    conversation = get_conversation_by_id(
        db=db,
        conversation_id=conversation_id,
    )

    if not conversation:
        await websocket.close(code=1008)
        return

    # Check whether user belongs to this conversation
    if (
        user.id != conversation.driver_id
        and user.id != conversation.passenger_id
    ):
        await websocket.close(code=1008)
        return

    await manager.connect(
        conversation_id,
        websocket,
    )

    try:
        while True:

            data = await websocket.receive_json()
            print('data = ',data)

            message = data.get("message")

            if not message:
                continue

            chat_message = chat_service.send_message_by_user_id(
                db=db,
                conversation_id=conversation_id,
                user_id=user.id,
                message=message,
)

            # Message to send to connected clients
            response = {
                "id": chat_message.id,
                "conversation_id": chat_message.conversation_id,
                "sender_id": chat_message.sender_id,
                "message": chat_message.message,
                "created_at": chat_message.created_at.isoformat(),
            }

            # Broadcast
            await manager.send_message(
                conversation_id,
                response,
            )

    except WebSocketDisconnect:

        manager.disconnect(
            conversation_id,
            websocket,
        )


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


# Look up conversation_id for a specific ride request.
# Both the driver and the passenger of the request can call this.
@router.get("/conversations/by-request/{ride_request_id}")
def get_conversation_by_request(
    ride_request_id: int,
    email: EmailStr = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conversation = chat_service.get_conversation_by_request(
        db=db,
        ride_request_id=ride_request_id,
        email=email,
    )
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail="No conversation found for this ride request.",
        )
    return {"conversation_id": conversation.id}
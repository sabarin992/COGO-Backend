from sqlalchemy import Column,Integer,ForeignKey,Text,DateTime
from datetime import datetime,timezone
from app.db.base import Base
from sqlalchemy.orm import relationship


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer,primary_key=True,index=True)
    conversation_id = Column(Integer,ForeignKey("chat_conversations.id"),nullable=False)
    sender_id = Column(Integer,ForeignKey("users.id"),nullable=False)
    message = Column(Text,nullable=False)
    created_at = Column(DateTime(timezone=True),default=lambda : datetime.now(timezone.utc),nullable=False)

    # relationships

    '''
    We can determine which conversation this message belongs to using the "conversation" variable
    '''
    conversation = relationship(
    "ChatConversation",
    back_populates="messages" #tells SQLAlchemy that both relationship attributes are two sides of the same relationship
)

    # get the sender who sent the message
    sender = relationship(
        "User",
         back_populates="sent_messages"
    )








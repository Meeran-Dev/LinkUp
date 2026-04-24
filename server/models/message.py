from sqlalchemy import *
from datetime import datetime
from database import Base
import enum

class ChatType(str,enum.Enum):
    dm="dm"
    global_chat="global"

class Message(Base):
    __tablename__="messages"

    id=Column(Integer,primary_key=True)
    sender_id=Column(Integer)

    chat_type=Column(Enum(ChatType))

    receiver_id=Column(Integer,nullable=True)
    group_id=Column(Integer,nullable=True)

    content=Column(Text)
    created_at=Column(DateTime,default=datetime.utcnow)
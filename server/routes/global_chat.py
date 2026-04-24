from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.message import Message, ChatType
from services.message import save_message
from pydantic import BaseModel

router = APIRouter(prefix="/global", tags=["global"])


class GlobalMessageRequest(BaseModel):
    sender_id: int
    content: str


@router.post("/message")
def send_global_message(payload: GlobalMessageRequest, db: Session = Depends(get_db)):
    """Send a message to the global chat"""
    message_data = {
        "sender_id": payload.sender_id,
        "chat_type": ChatType.global_chat.value,
        "content": payload.content
    }
    msg = save_message(db, message_data)
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }


@router.get("/messages")
def get_global_messages(limit: int = 50, db: Session = Depends(get_db)):
    """Get global chat messages"""
    messages = db.query(Message).filter(
        Message.chat_type == ChatType.global_chat.value
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]
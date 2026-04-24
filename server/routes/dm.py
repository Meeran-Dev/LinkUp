from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.message import Message, ChatType
from services.message import save_message
from services.notification import create_notification
from pydantic import BaseModel

router = APIRouter(prefix="/dm", tags=["dm"])


class DmRequest(BaseModel):
    sender_id: int
    receiver_id: int
    content: str


class DmResponse(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/send")
def send_dm(payload: DmRequest, db: Session = Depends(get_db)):
    """Send a direct message"""
    message_data = {
        "sender_id": payload.sender_id,
        "chat_type": ChatType.dm.value,
        "receiver_id": payload.receiver_id,
        "content": payload.content
    }
    msg = save_message(db, message_data)
    
    # Create notification for receiver
    create_notification(
        payload.receiver_id,
        "new_message",
        {"sender_id": payload.sender_id, "content": payload.content}
    )
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }


@router.get("/history/{user_id}/{other_id}")
def get_dm_history(user_id: int, other_id: int, db: Session = Depends(get_db)):
    """Get direct message history between two users"""
    messages = db.query(Message).filter(
        ((Message.sender_id == user_id) & (Message.receiver_id == other_id)) |
        ((Message.sender_id == other_id) & (Message.receiver_id == user_id))
    ).filter(
        Message.chat_type == ChatType.dm
    ).order_by(Message.created_at.desc()).limit(50).all()
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]
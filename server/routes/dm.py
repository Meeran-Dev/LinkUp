from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models.message import Message, ChatType
from services.message import save_message
from services.notification import create_notification
from websocket.events import publish_message
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

    from models.user import User
    sender = db.query(User).filter(User.id == payload.sender_id).first()
    publish_message({
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "chat_type": msg.chat_type.value,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
        "sender_name": sender.username if sender else "User"
    })
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }


@router.get("/messages")
def get_dm_history(sender_id: int, receiver_id: int, db: Session = Depends(get_db)):
    """Get direct message history between two users"""
    from models.user import User
    
    messages = db.query(Message).filter(
        ((Message.sender_id == sender_id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == sender_id))
    ).filter(
        Message.chat_type == ChatType.dm
    ).order_by(Message.created_at.asc()).limit(50).all()
    
    # Get user info for sender names
    user_ids = set(m.sender_id for m in messages)
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u.username for u in users}
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": user_map.get(m.sender_id, "User"),
            "receiver_id": m.receiver_id,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]


@router.get("/conversations/{user_id}")
def get_user_conversations(user_id: int, db: Session = Depends(get_db)):
    """Get all DM conversations for a user"""
    # Get all unique users the user has messaged with
    sent_messages = db.query(Message).filter(
        Message.sender_id == user_id,
        Message.chat_type == ChatType.dm
    ).all()
    
    received_messages = db.query(Message).filter(
        Message.receiver_id == user_id,
        Message.chat_type == ChatType.dm
    ).all()
    
    # Get unique user IDs
    user_ids = set()
    for msg in sent_messages:
        user_ids.add(msg.receiver_id)
    for msg in received_messages:
        user_ids.add(msg.sender_id)
    
    # Get user details
    from models.user import User
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    
    # Get last message for each conversation
    conversations = []
    for u in users:
        last_msg = db.query(Message).filter(
            ((Message.sender_id == user_id) & (Message.receiver_id == u.id)) |
            ((Message.sender_id == u.id) & (Message.receiver_id == user_id))
        ).filter(Message.chat_type == ChatType.dm).order_by(Message.created_at.desc()).first()
        
        conversations.append({
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "last_message": last_msg.content if last_msg else None,
            "last_message_at": last_msg.created_at.isoformat() if last_msg else None
        })
    
    # Sort by last message time
    conversations.sort(key=lambda x: x["last_message_at"] or "", reverse=True)
    
    return conversations
from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session
from database import get_db
from models.group import GroupChat
from models.message import Message, ChatType
from services.message import save_message
from schemas.group import GroupCreate, GroupResponse, GroupMessage

router=APIRouter(prefix="/groups")

@router.post("/create", response_model=GroupResponse)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):

    group=GroupChat(
      name=payload.name,
      created_by=payload.creator_id
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    return GroupResponse(
        id=group.id,
        name=group.name,
        created_by=group.created_by,
        created_at=group.created_at
    )


@router.get("/{group_id}/messages")
def get_group_messages(group_id: int, limit: int = 50, db: Session = Depends(get_db)):
    """Get messages for a specific group"""
    messages = db.query(Message).filter(
        Message.group_id == group_id,
        Message.chat_type == ChatType.dm  # Using dm type for group messages
    ).order_by(Message.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "group_id": m.group_id,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        }
        for m in messages
    ]


@router.post("/message")
def send_group_message(payload: GroupMessage, db: Session = Depends(get_db)):
    """Send a message to a group"""
    # Verify group exists
    group = db.query(GroupChat).filter(GroupChat.id == payload.group_id).first()
    if not group:
        return {"error": "Group not found"}, 404
    
    message_data = {
        "sender_id": payload.sender_id,
        "chat_type": "dm",  # Using dm type for group messages
        "group_id": payload.group_id,
        "content": payload.content
    }
    msg = save_message(db, message_data)
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "group_id": msg.group_id,
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }
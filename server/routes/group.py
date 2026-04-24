from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.group import GroupChat, group_members
from models.message import Message, ChatType
from services.message import save_message
from schemas.group import GroupCreate, GroupResponse, GroupMessage
from pydantic import BaseModel

router=APIRouter(prefix="/groups")


class AddMemberRequest(BaseModel):
    user_id: int

@router.post("/create", response_model=GroupResponse)
def create_group(payload: GroupCreate, db: Session = Depends(get_db)):

    group=GroupChat(
      name=payload.name,
      created_by=payload.creator_id
    )

    db.add(group)
    db.commit()
    db.refresh(group)

    # Add creator as a member
    db.execute(group_members.insert().values(
        user_id=payload.creator_id,
        group_id=group.id
    ))
    db.commit()

    return GroupResponse(
        id=group.id,
        name=group.name,
        created_by=group.created_by,
        created_at=group.created_at
    )


@router.get("/list")
def list_user_groups(user_id: int, db: Session = Depends(get_db)):
    """List all groups a user is a member of"""
    # Get groups where user is a member
    member_groups = db.query(group_members).filter(
        group_members.c.user_id == user_id
    ).all()
    
    group_ids = [m.group_id for m in member_groups]
    
    # Also get groups created by user
    created_groups = db.query(GroupChat).filter(
        GroupChat.created_by == user_id
    ).all()
    
    for g in created_groups:
        if g.id not in group_ids:
            group_ids.append(g.id)
    
    # Fetch group details
    groups = db.query(GroupChat).filter(GroupChat.id.in_(group_ids)).all()
    
    return [
        {
            "id": g.id,
            "name": g.name,
            "created_by": g.created_by,
            "created_at": g.created_at.isoformat() if g.created_at else None
        }
        for g in groups
    ]


@router.get("/{group_id}/messages")
def get_group_messages(group_id: int, limit: int = 50, db: Session = Depends(get_db)):
    messages = db.query(Message).filter(
        Message.group_id == group_id,
        Message.chat_type == ChatType.dm  # Using dm type for group messages
    ).order_by(Message.created_at.asc()).limit(limit).all()
    
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


@router.post("/{group_id}/members")
def add_group_member(group_id: int, payload: AddMemberRequest, db: Session = Depends(get_db)):
    user_id = payload.user_id
    # Check if group exists
    group = db.query(GroupChat).filter(GroupChat.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if user exists
    from models.user import User
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if already a member
    existing = db.query(group_members).filter(
        group_members.c.group_id == group_id,
        group_members.c.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="User is already a member")
    
    # Add member
    db.execute(group_members.insert().values(
        user_id=user_id,
        group_id=group_id
    ))
    db.commit()
    
    return {"message": "Member added successfully"}


@router.get("/{group_id}/members")
def get_group_members(group_id: int, db: Session = Depends(get_db)):
    """Get all members of a group"""
    members = db.query(group_members).filter(
        group_members.c.group_id == group_id
    ).all()
    
    from models.user import User
    user_ids = [m.user_id for m in members]
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email
        }
        for u in users
    ]
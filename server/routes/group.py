from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from database import get_db
from models.group import GroupChat, group_members
from models.message import Message, ChatType
from services.message import save_message
from websocket.events import publish_message
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
    from models.user import User
    
    messages = db.query(Message).filter(
        Message.group_id == group_id,
        Message.chat_type == ChatType.group
    ).order_by(Message.created_at.asc()).limit(limit).all()
    
    # Get user info for sender names
    user_ids = set(m.sender_id for m in messages)
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    user_map = {u.id: u.username for u in users}
    
    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "sender_name": user_map.get(m.sender_id, "User"),
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
        "chat_type": ChatType.group.value,
        "group_id": payload.group_id,
        "content": payload.content
    }
    msg = save_message(db, message_data)

    from models.user import User
    sender = db.query(User).filter(User.id == payload.sender_id).first()
    publish_message({
        "sender_id": msg.sender_id,
        "group_id": msg.group_id,
        "chat_type": msg.chat_type.value,
        "content": msg.content,
        "created_at": msg.created_at.isoformat(),
        "sender_name": sender.username if sender else "User"
    })
    
    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "group_id": msg.group_id,
        "content": msg.content,
        "created_at": msg.created_at.isoformat()
    }


@router.post("/{group_id}/members")
def add_group_member(group_id: int, payload: AddMemberRequest, creator_id: int, db: Session = Depends(get_db)):
    """Add a member to a group (only the creator can add members)"""
    user_id = payload.user_id
    # Check if group exists
    group = db.query(GroupChat).filter(GroupChat.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if the requester is the group creator
    if group.created_by != creator_id:
        raise HTTPException(status_code=403, detail="Only the group creator can add members")
    
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
    """Get all members of a group including the creator"""
    from models.user import User
    
    # Get current members
    members = db.query(group_members).filter(
        group_members.c.group_id == group_id
    ).all()
    
    user_ids = [m.user_id for m in members]
    
    # Get the group to find the creator
    group = db.query(GroupChat).filter(GroupChat.id == group_id).first()
    if group and group.created_by not in user_ids:
        user_ids.append(group.created_by)
    
    # Fetch user details
    users = db.query(User).filter(User.id.in_(user_ids)).all() if user_ids else []
    
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "is_admin": u.id == group.created_by if group else False
        }
        for u in users
    ]


@router.delete("/{group_id}")
def delete_group(group_id: int, creator_id: int, db: Session = Depends(get_db)):
    """Delete a group (only the creator can delete)"""
    group = db.query(GroupChat).filter(GroupChat.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if the requester is the group creator
    if group.created_by != creator_id:
        raise HTTPException(status_code=403, detail="Only the group creator can delete this group")
    
    # Delete all messages in the group
    db.query(Message).filter(Message.group_id == group_id).delete()
    
    # Delete all members
    db.execute(group_members.delete().where(group_members.c.group_id == group_id))
    
    # Delete the group
    db.delete(group)
    db.commit()
    
    return {"message": "Group deleted successfully"}


@router.delete("/{group_id}/members/{user_id}")
def remove_group_member(group_id: int, user_id: int, creator_id: int, db: Session = Depends(get_db)):
    """Remove a member from a group (only the creator can remove members)"""
    from models.user import User
    
    # Check if group exists
    group = db.query(GroupChat).filter(GroupChat.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")
    
    # Check if the requester is the group creator
    if group.created_by != creator_id:
        raise HTTPException(status_code=403, detail="Only the group creator can remove members")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is a member
    existing = db.query(group_members).filter(
        group_members.c.group_id == group_id,
        group_members.c.user_id == user_id
    ).first()
    
    if not existing:
        raise HTTPException(status_code=400, detail="User is not a member of this group")
    
    # Remove member
    db.execute(group_members.delete().where(
        group_members.c.group_id == group_id,
        group_members.c.user_id == user_id
    ))
    db.commit()
    
    return {"message": "Member removed successfully"}
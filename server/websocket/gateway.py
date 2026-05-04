from fastapi import APIRouter,WebSocket
from .manager import manager
from database import SessionLocal
from models.group import group_members
import json

router=APIRouter()

@router.websocket("/ws/{user_id}")
async def websocket_chat(
 user_id:int,
 websocket:WebSocket
):

    await manager.connect(
      user_id,
      websocket
    )

    manager.join_room(
      user_id,
      "global_chat"
    )

    db = SessionLocal()
    try:
        groups = db.query(group_members.c.group_id).filter(group_members.c.user_id == user_id).all()
        for group in groups:
            manager.join_room(user_id, f"group:{group.group_id}")
    finally:
        db.close()

    try:
      while True:
          data=await websocket.receive_json()

          event={
             "sender_id":user_id,
             **data
          }

          publish_message(event)

    except:
       manager.disconnect(user_id)
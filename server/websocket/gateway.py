from fastapi import APIRouter,WebSocket
from manager import manager
from events import publish_message
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
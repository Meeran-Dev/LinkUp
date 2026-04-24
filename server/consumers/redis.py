import redis
import json
import asyncio

from websocket.manager import manager
from config import settings

r=redis.Redis.from_url(
 settings.REDIS_URL,
 decode_responses=True
)

pubsub=r.pubsub()
pubsub.subscribe("chat_events")

async def consume_events():

    while True:

        msg=pubsub.get_message()

        if msg and msg["type"]=="message":

            payload=json.loads(
                msg["data"]
            )

            chat_type=payload["chat_type"]

            if chat_type=="dm":
                await manager.send_to_user(
                  payload["receiver_id"],
                  payload
                )
            
            elif chat_type=="group":
                room=f"group:{payload['group_id']}"
                await manager.broadcast_room(
                   room,
                   payload
                )

            elif chat_type=="global":
                await manager.broadcast_room(
                   "global_chat",
                   payload
                )

        await asyncio.sleep(.1)
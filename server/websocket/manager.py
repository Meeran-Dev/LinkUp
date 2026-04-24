from collections import defaultdict
from fastapi import WebSocket

class ConnectionManager:

    def __init__(self):
        self.user_connections={}

        self.rooms=defaultdict(set)

    async def connect(
        self,
        user_id,
        websocket:WebSocket
    ):
        await websocket.accept()
        self.user_connections[user_id]=websocket
    
    def disconnect(self,user_id):
        if user_id in self.user_connections:
            del self.user_connections[user_id]

    def join_room(self,user_id,room):
        self.rooms[room].add(user_id)

    def leave_room(self,user_id,room):
        self.rooms[room].discard(user_id)

    async def send_to_user(
       self,
       user_id,
       payload
    ):
        if user_id in self.user_connections:
            await self.user_connections[user_id].send_json(
                payload
            )
    
    async def broadcast_room(
       self,
       room,
       payload
    ):
        users=self.rooms[room]

        for uid in users:
            if uid in self.user_connections:
                await self.user_connections[
                    uid
                ].send_json(payload)

manager=ConnectionManager()
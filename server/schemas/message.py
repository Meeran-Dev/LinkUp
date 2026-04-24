from pydantic import BaseModel
from typing import Optional

class MessageCreate(BaseModel):
    chat_type:str
    receiver_id:Optional[int]=None
    group_id:Optional[int]=None
    content:str
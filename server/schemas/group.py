from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GroupCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    creator_id: int


class GroupResponse(BaseModel):
    id: int
    name: str
    created_by: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GroupMemberAdd(BaseModel):
    user_id: int
    group_id: int


class GroupMessage(BaseModel):
    sender_id: int
    group_id: int
    content: str = Field(..., min_length=1)


class GroupMessageResponse(BaseModel):
    id: int
    sender_id: int
    group_id: int
    content: str
    created_at: str

    class Config:
        from_attributes = True
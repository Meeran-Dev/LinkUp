from datetime import datetime
from sqlalchemy import *
from database import Base

group_members=Table(
    "group_members",
    Base.metadata,
    Column("user_id",Integer,ForeignKey("users.id")),
    Column("group_id",Integer,ForeignKey("groups.id"))
)

class GroupChat(Base):
    __tablename__="groups"

    id=Column(Integer,primary_key=True)
    name=Column(String)
    created_by=Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
from jose import jwt
from datetime import datetime,timedelta
from passlib.context import CryptContext
from config import settings

pwd=CryptContext(schemes=["bcrypt"])

def hash_password(p):
    return pwd.hash(p)

def verify_password(p,h):
    return pwd.verify(p,h)

def create_token(data):
    payload=data.copy()
    payload["exp"]=datetime.utcnow()+timedelta(days=1)
    return jwt.encode(
      payload,
      settings.SECRET_KEY,
      algorithm=settings.ALGORITHM
    )
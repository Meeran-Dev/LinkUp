import redis
from config import settings

r = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

def set_user_online(user_id: int):
    r.sadd("online_users", user_id)
    r.hset("user_presence", user_id, "status", "online")

def set_user_offline(user_id: int):
    r.srem("online_users", user_id)
    r.hset("user_presence", user_id, "status", "offline")

def get_online_users():
    return list(r.smembers("online_users"))

def is_user_online(user_id: int) -> bool:
    return r.sismember("online_users", user_id)

def get_user_presence(user_id: int) -> str:
    return r.hget("user_presence", user_id) or "offline"
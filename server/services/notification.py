import redis
import json
from config import settings

r = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True
)

def create_notification(user_id: int, notification_type: str, data: dict):
    notification = {
        "type": notification_type,
        "data": data,
        "read": False
    }
    r.lpush(f"notifications:{user_id}", json.dumps(notification))
    return notification

def get_notifications(user_id: int, limit: int = 50):
    notifications = r.lrange(f"notifications:{user_id}", 0, limit - 1)
    return [json.loads(n) for n in notifications]

def mark_notification_read(user_id: int, index: int):
    key = f"notifications:{user_id}"
    notification = r.lindex(key, index)
    if notification:
        data = json.loads(notification)
        data["read"] = True
        r.lset(key, index, json.dumps(data))

def get_unread_count(user_id: int) -> int:
    notifications = r.lrange(f"notifications:{user_id}", 0, -1)
    unread = 0
    for n in notifications:
        data = json.loads(n)
        if not data.get("read", False):
            unread += 1
    return unread

def clear_notifications(user_id: int):
    r.delete(f"notifications:{user_id}")
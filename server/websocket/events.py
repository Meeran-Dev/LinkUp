import redis
import json
from config import settings

r=redis.Redis.from_url(
 settings.REDIS_URL,
 decode_responses=True
)

def publish_message(event):
    r.publish(
      "chat_events",
      json.dumps(event)
    )
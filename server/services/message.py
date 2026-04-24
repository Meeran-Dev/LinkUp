from models.message import Message

def save_message(db,payload):

  msg=Message(
      sender_id=payload["sender_id"],
      chat_type=payload["chat_type"],
      receiver_id=payload.get("receiver_id"),
      group_id=payload.get("group_id"),
      content=payload["content"]
    )

  db.add(msg)
  db.commit()

  return msg
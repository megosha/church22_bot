import json

from redis import Redis
from settings import get_env_value

db = Redis.from_url(get_env_value('REDIS'))


class RDB():
    def init_item(self, chat_id, tm_id, name, m_id):
        structure =             {"tm_id": tm_id,
                     "name": name,
                     "chat_id": chat_id,
                     "last_message_id": m_id,
                     "request": 0
                     }

        return structure

    def set_item(self, chat_id, body: dict):
        for key, value in body.items():
            db.hset(chat_id, key, value)
        # return db.set(chat_id, body)

    def get_item(self, chat_id: int, key):
        return db.hget(chat_id, key).decode()

    def change_item(self, chat_id: int, key: str, val: str):
        db.hset(chat_id, key, val)

    def remove_all(self):
        for key in db.scan_iter('*'):
            db.delete(key)

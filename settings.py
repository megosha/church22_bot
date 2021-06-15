import json
import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
ACTIONS = json.loads(os.environ.get('ACTIONS'))


def get_env_value(key):
    return os.environ.get(key)

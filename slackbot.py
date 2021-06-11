import requests
from settings import WEBHOOK_URL
import json


def post_message(message: str):
    message = {
        "text": message
    }
    return requests.post(WEBHOOK_URL, data = json.dumps(message))


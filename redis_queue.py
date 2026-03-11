import json
import os
import redis
from datetime import datetime

REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))
QUEUE_KEY = 'events-queue'

_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)


def publish_event(event_type: str, source: str, description: str):
    payload = {
        'type': event_type,
        'source': source,
        'description': description,
        'date': datetime.utcnow().isoformat(),
    }
    _client.rpush(QUEUE_KEY, json.dumps(payload))

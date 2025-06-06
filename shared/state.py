import redis
import json

r = redis.Redis()

def add_item(item):
    r.rpush("incidents_queue", json.dumps(item))

def pop_item():
    data = r.lpop("incidents_queue")
    if data is not None:
        return json.loads(data)
    return None
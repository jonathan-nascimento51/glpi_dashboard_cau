# Configurações do Backend

import os

import redis

# ...outras configurações...


def get_redis_connection():
    try:
        return redis.StrictRedis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True,
        )
    except redis.ConnectionError as e:
        print(f"⚠️ Redis connection failed: {e}")
        return None


# ...código existente...

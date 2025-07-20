# Configurações do Backend

import logging
import os

import redis

# ...outras configurações...


def get_redis_connection():
    try:
        return redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=int(os.getenv("REDIS_DB", 0)),
            decode_responses=True,
        )
    except redis.ConnectionError as e:
        logging.getLogger(__name__).warning("⚠️ Redis connection failed: %s", e)
        return None


# ...código existente...

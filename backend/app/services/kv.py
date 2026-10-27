"""Tiny key-value layer: Redis when it's running, otherwise an in-memory dict with expiry.

Used for response caching and rate limiting, so neither needs Redis to work locally.
"""
import logging
import time

from app.config import settings

log = logging.getLogger(__name__)


class MemoryKV:
    name = "memory"

    def __init__(self):
        self._data: dict[str, tuple[str, float]] = {}

    def _alive(self, key):
        item = self._data.get(key)
        if item and item[1] < time.time():
            del self._data[key]
            return None
        return item

    def get(self, key):
        item = self._alive(key)
        return item[0] if item else None

    def set(self, key, value, ttl):
        self._data[key] = (value, time.time() + ttl)

    def incr(self, key, ttl):
        item = self._alive(key)
        count = int(item[0]) + 1 if item else 1
        self._data[key] = (str(count), item[1] if item else time.time() + ttl)
        return count


class RedisKV:
    name = "redis"

    def __init__(self, client):
        self._r = client

    def get(self, key):
        return self._r.get(key)

    def set(self, key, value, ttl):
        self._r.set(key, value, ex=ttl)

    def incr(self, key, ttl):
        pipe = self._r.pipeline()
        pipe.incr(key)
        pipe.expire(key, ttl, nx=True)  # only set expiry when the key is new
        return pipe.execute()[0]


def connect():
    try:
        import redis

        client = redis.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=1)
        client.ping()
        log.info("Using Redis at %s", settings.redis_url)
        return RedisKV(client)
    except Exception as exc:
        log.warning("Redis unavailable (%s); using in-memory cache and rate limiter", type(exc).__name__)
        return MemoryKV()


kv = connect()

"""Fixed-window rate limiter: N requests per client per minute."""
import time

from fastapi import HTTPException, Request

from app.config import settings
from app.services import kv as kv_module
from app.services.metrics import RATE_LIMITED


def rate_limit(request: Request):
    client = request.client.host if request.client else "unknown"
    window = int(time.time() // 60)
    count = kv_module.kv.incr(f"rl:{client}:{window}", ttl=60)
    if count > settings.rate_limit_per_minute:
        RATE_LIMITED.inc()
        raise HTTPException(429, "Too many requests. Try again in a minute.",
                            headers={"Retry-After": str(60 - int(time.time()) % 60)})

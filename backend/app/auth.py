"""Demo JWT auth. Real Google OAuth replaces this later."""
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


def create_token(subject: str, hours: int = 24) -> str:
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(hours=hours)}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def verify_token(token: str) -> str:
    """Returns the user id, or raises jwt.InvalidTokenError."""
    data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    return data["sub"]

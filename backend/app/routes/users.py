"""Auth and per-user usage. Stored in memory for now; Phase 5 moves this to a database."""
from collections import Counter, defaultdict

import jwt
from fastapi import APIRouter, Header, HTTPException

from app.auth import create_token, verify_token
from app.config import settings
from app.schemas import UsageEvent

router = APIRouter(prefix="/api", tags=["users"])
_usage: dict[str, Counter] = defaultdict(Counter)


def current_user(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "Missing bearer token")
    try:
        return verify_token(authorization.removeprefix("Bearer "))
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid or expired token")


@router.post("/auth/demo-token")
def demo_token():
    return {"access_token": create_token(settings.demo_auth_subject), "token_type": "bearer"}


@router.get("/users/me/usage")
def get_usage(authorization: str | None = Header(None)):
    return dict(_usage[current_user(authorization)])


@router.post("/users/me/usage")
def add_usage(event: UsageEvent, authorization: str | None = Header(None)):
    user = current_user(authorization)
    _usage[user][event.action] += 1
    return dict(_usage[user])


@router.delete("/users/me")
def delete_me(authorization: str | None = Header(None)):
    """Deletes everything stored about the user."""
    _usage.pop(current_user(authorization), None)
    return {"deleted": True}

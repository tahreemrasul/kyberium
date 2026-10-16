"""Anonymous wardrobe ownership.

POST /session issues a random bearer token. The wardrobe owner id is a hash of
that token, so the server never stores the token and a client cannot address
another owner's records by guessing ids: every query is scoped by the owner id
derived from the presented token, never by an id supplied in the request.
"""

import hashlib
import re
import secrets

from fastapi import Header

from app.errors import ApiError

_TOKEN_RE = re.compile(r"^rw_[A-Za-z0-9_-]{32,64}$")


def new_token() -> str:
    return "rw_" + secrets.token_urlsafe(32)


def owner_id_for(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()[:32]


async def get_owner(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise ApiError(401, "unauthorized", "Missing session token. Call POST /session first.")
    token = authorization.removeprefix("Bearer ").strip()
    if not _TOKEN_RE.match(token):
        raise ApiError(401, "unauthorized", "Invalid session token.")
    return owner_id_for(token)

"""FastAPI dependencies (overridable in tests) and a small per-owner rate limit for AI calls."""

import time
from collections import defaultdict, deque

from fastapi import Depends

from app.ai.client import GeminiClient, get_ai
from app.auth import get_owner
from app.config import Settings, get_settings
from app.errors import ApiError
from app.knowledge import FashionKnowledgeRetriever, get_retriever
from app.storage import BlobStore, Repository, get_blobs, get_repo


def repo_dep() -> Repository:
    return get_repo()


def blobs_dep() -> BlobStore:
    return get_blobs()


def ai_dep() -> GeminiClient | None:
    return get_ai()


def retriever_dep() -> FashionKnowledgeRetriever:
    return get_retriever()


def settings_dep() -> Settings:
    return get_settings()


_WINDOW_S = 60.0
_MAX_AI_CALLS = 30
_calls: dict[str, deque[float]] = defaultdict(deque)


async def ai_budget(owner: str = Depends(get_owner)) -> str:
    """Budget guard: at most _MAX_AI_CALLS AI-backed requests per owner per minute (per instance)."""
    now = time.monotonic()
    q = _calls[owner]
    while q and now - q[0] > _WINDOW_S:
        q.popleft()
    if len(q) >= _MAX_AI_CALLS:
        raise ApiError(429, "rate_limited", "You're styling fast! Please wait a moment and try again.", retryable=True)
    q.append(now)
    return owner

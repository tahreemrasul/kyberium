from fastapi import APIRouter, Depends

from app import __version__
from app.auth import new_token
from app.config import Settings
from app.deps import settings_dep
from app.schemas import Health, Session

router = APIRouter(tags=["system"])


@router.get("/health", response_model=Health)
async def health(settings: Settings = Depends(settings_dep)) -> Health:
    return Health(
        status="ok",
        version=__version__,
        ai_enabled=settings.ai_enabled,
        ai_model=settings.gemini_model if settings.ai_enabled else None,
        storage_backend=settings.storage_backend,
        knowledge_backend=settings.fashion_knowledge_backend,
    )


@router.post("/session", response_model=Session)
async def create_session() -> Session:
    """Issue an anonymous wardrobe token. Keep it client-side; it is the only key to that closet."""
    return Session(token=new_token())

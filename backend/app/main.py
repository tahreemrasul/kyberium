"""Rewear API — FastAPI entrypoint (uvicorn app.main:app)."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import get_settings
from app.errors import install_error_handlers
from app.routers import demo, inspirations, looks, media, system, wardrobe

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="Rewear API",
        version=__version__,
        description="Reuse-first AI styling: recreate inspiration outfits from your own wardrobe.",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
    install_error_handlers(app)
    for r in (system, wardrobe, demo, inspirations, looks, media):
        app.include_router(r.router)
    logging.getLogger("rewear").info(
        "starting rewear api ai_enabled=%s model=%s storage=%s knowledge=%s",
        settings.ai_enabled,
        settings.gemini_model,
        settings.storage_backend,
        settings.fashion_knowledge_backend,
    )
    return app


app = create_app()

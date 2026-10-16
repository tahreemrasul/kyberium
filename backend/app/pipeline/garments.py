"""Step 1 — garment understanding (photo -> validated GarmentDraft), cached by image hash."""

import hashlib
import logging

from app.ai.client import AIError, GeminiClient
from app.ai.prompts import GARMENT_SYSTEM, PROMPT_VERSION
from app.schemas import GarmentAnalysis, GarmentDraft
from app.storage import Repository

log = logging.getLogger("rewear")
CACHE = "analysis_cache"


def cache_key(kind: str, image_sha: str, model: str) -> str:
    return kind + "_" + hashlib.sha256(f"{image_sha}|{PROMPT_VERSION}|{model}".encode()).hexdigest()[:48]


async def analyze_garment(
    ai: GeminiClient | None,
    repo: Repository,
    owner: str,
    *,
    upload_id: str,
    image_url: str,
    image: bytes,
    image_sha: str,
) -> GarmentAnalysis:
    if ai is None:
        return GarmentAnalysis(
            upload_id=upload_id,
            image_url=image_url,
            draft=None,
            engine="none",
            message="AI tagging isn't available in demo mode. Add the details yourself — it only takes a moment.",
        )
    key = cache_key("g", image_sha, ai.settings.gemini_model)
    cached = await repo.get(owner, CACHE, key)
    if cached:
        return GarmentAnalysis(
            upload_id=upload_id,
            image_url=image_url,
            draft=GarmentDraft.model_validate(cached),
            engine="gemini",
            cached=True,
        )
    try:
        draft = await ai.generate_json(
            schema=GarmentDraft,
            system=GARMENT_SYSTEM,
            contents=[ai.image_part(image, "image/jpeg"), "Catalogue this garment."],
            temperature=0.2,
            thinking_budget=0,
            label="garment",
        )
    except AIError as exc:
        return GarmentAnalysis(
            upload_id=upload_id,
            image_url=image_url,
            draft=None,
            engine="none",
            message=f"{exc.message} Your photo is saved — retry tagging or fill in the details yourself.",
        )
    await repo.put(owner, CACHE, key, draft.model_dump())
    message = None
    if not draft.is_garment:
        message = draft.notes or "This photo doesn't look like a single clothing item. Please check the details."
    return GarmentAnalysis(upload_id=upload_id, image_url=image_url, draft=draft, engine="gemini", message=message)

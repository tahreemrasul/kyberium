"""Step 2 — inspiration understanding (outfit photo -> InspirationAnalysis), cached by image hash."""

from app.ai.client import AIError, AIUnavailable, GeminiClient
from app.ai.prompts import INSPIRATION_SYSTEM
from app.errors import ApiError
from app.pipeline.garments import CACHE, cache_key
from app.schemas import InspirationAnalysis
from app.storage import Repository


def normalise_slots(analysis: InspirationAnalysis) -> InspirationAnalysis:
    """Guarantee unique, predictable slot ids regardless of what the model returned."""
    counts: dict[str, int] = {}
    for piece in analysis.pieces:
        counts[piece.category] = counts.get(piece.category, 0) + 1
        piece.slot_id = f"{piece.category}-{counts[piece.category]}"
    if not analysis.pieces:
        analysis.is_outfit = False
    return analysis


async def analyze_inspiration(
    ai: GeminiClient | None, repo: Repository, owner: str, *, image: bytes, image_sha: str
) -> InspirationAnalysis:
    if ai is None:
        raise ApiError(
            503,
            AIUnavailable().code,
            "Live inspiration analysis needs Gemini, which isn't configured here. Try one of the sample inspirations.",
        )
    key = cache_key("i", image_sha, ai.settings.gemini_model)
    cached = await repo.get(owner, CACHE, key)
    if cached:
        return InspirationAnalysis.model_validate(cached)
    try:
        analysis = await ai.generate_json(
            schema=InspirationAnalysis,
            system=INSPIRATION_SYSTEM,
            contents=[ai.image_part(image, "image/jpeg"), "Deconstruct this inspiration outfit."],
            temperature=0.3,
            thinking_budget=512,
            label="inspiration",
        )
    except AIError as exc:
        raise ApiError(503, exc.code, exc.message, retryable=exc.retryable) from exc
    analysis = normalise_slots(analysis)
    await repo.put(owner, CACHE, key, analysis.model_dump())
    return analysis

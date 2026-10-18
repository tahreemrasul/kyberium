"""The styling pipeline:

inspiration analysis -> optional knowledge retrieval -> deterministic wardrobe
retrieval -> Gemini (or labelled rule-based) composition -> validation ->
gap & impact assessment -> persisted Generation.
"""

import logging
import uuid
from datetime import UTC, datetime

from app.ai.client import AIError, GeminiClient
from app.config import Settings
from app.errors import ApiError
from app.knowledge import FashionKnowledgeRetriever, build_query, safe_search
from app.pipeline.composer import compose_with_gemini, compose_with_rules
from app.pipeline.retrieval import rank_candidates
from app.pipeline.validation import build_looks
from app.schemas import Garment, Generation, InspirationAnalysis, KnowledgeHitRef, StylePreferences
from app.storage import Repository

log = logging.getLogger("rewear")
GENERATIONS = "generations"

DEMO_NOTE = (
    "Demo mode: Gemini isn't configured on this deployment, so these looks come from Rewear's "
    "rule-based matcher. Explanations are templated."
)
FALLBACK_NOTE = (
    "Our AI stylist was unavailable ({reason}), so these looks come from Rewear's rule-based "
    "matcher. Try again for AI-written styling."
)


async def run_pipeline(
    *,
    ai: GeminiClient | None,
    settings: Settings,
    retriever: FashionKnowledgeRetriever,
    wardrobe: dict[str, Garment],
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
    inspiration_id: str,
    inspiration_image_url: str,
    generation_id: str | None = None,
    extra_note: str | None = None,
) -> Generation:
    if not wardrobe:
        raise ApiError(409, "empty_wardrobe", "Your closet is empty. Add a few garments or load the sample wardrobe.")
    # Ignore ids the user does not own; they can never influence the result.
    prefs = prefs.model_copy(
        update={
            "keep_garment_ids": [g for g in prefs.keep_garment_ids if g in wardrobe],
            "exclude_garment_ids": [g for g in prefs.exclude_garment_ids if g in wardrobe],
        }
    )
    now = datetime.now(UTC)
    gen_id = generation_id or "gen_" + uuid.uuid4().hex[:16]

    if not analysis.is_outfit or not analysis.pieces:
        return Generation(
            id=gen_id,
            inspiration_id=inspiration_id,
            inspiration_image_url=inspiration_image_url,
            analysis=analysis,
            preferences=prefs,
            looks=[],
            candidates={},
            engine="gemini" if ai else "rules",
            no_match_reason="We couldn't find a wearable outfit in this image. Try a clearer full-outfit photo.",
            created_at=now,
        )

    candidates = rank_candidates(analysis, list(wardrobe.values()), prefs)
    hits = await safe_search(
        retriever,
        build_query(analysis, prefs),
        top_k=settings.fashion_knowledge_top_k,
        timeout_s=settings.fashion_knowledge_timeout_s,
    )

    engine = "rules"
    note: str | None = None
    looks = []
    no_match: str | None = None
    if ai is not None:
        try:
            result = await compose_with_gemini(ai, analysis, prefs, candidates, wardrobe, hits)
            looks = build_looks(result.looks, wardrobe, analysis, prefs)
            no_match = result.no_match_reason
            engine = "gemini"
            if not looks and result.looks:
                raise AIError("ai_invalid_looks", "every suggested look failed validation", retryable=True)
        except AIError as exc:
            log.warning("composer failed: %s", exc.message)
            if settings.composer_fallback != "rules":
                raise ApiError(503, exc.code, exc.message, retryable=exc.retryable) from exc
            engine, note = "rules", FALLBACK_NOTE.format(reason=exc.message.rstrip("."))
            looks = []
    else:
        note = DEMO_NOTE

    if engine == "rules":
        result = compose_with_rules(analysis, prefs, candidates, wardrobe)
        looks = build_looks(result.looks, wardrobe, analysis, prefs)
        no_match = result.no_match_reason

    if not looks and not no_match:
        no_match = "None of your garments are a reasonable match for this outfit's key pieces."

    return Generation(
        id=gen_id,
        inspiration_id=inspiration_id,
        inspiration_image_url=inspiration_image_url,
        analysis=analysis,
        preferences=prefs,
        looks=looks,
        candidates=candidates,
        engine=engine,
        engine_note=" ".join(n for n in (extra_note, note) if n) or None,
        no_match_reason=no_match if not looks else None,
        knowledge=[
            KnowledgeHitRef(id=h.id, text=h.text, source_title=h.source_title, source_url=h.source_url) for h in hits
        ],
        created_at=now,
    )


async def save_generation(repo: Repository, owner: str, gen: Generation) -> None:
    await repo.put(owner, GENERATIONS, gen.id, gen.model_dump(mode="json"))


async def load_generation(repo: Repository, owner: str, gen_id: str) -> Generation:
    try:
        doc = await repo.get(owner, GENERATIONS, gen_id)
    except ValueError:
        doc = None
    if not doc:
        raise ApiError(404, "not_found", "That styling session was not found.")
    return Generation.model_validate(doc)

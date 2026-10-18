import pytest

from app.ai.client import AIError
from app.config import Settings
from app.demo import SAMPLE_INSPIRATION_INDEX
from app.errors import ApiError
from app.knowledge import NoOpFashionKnowledgeRetriever
from app.pipeline.orchestrator import run_pipeline
from app.pipeline.refine import apply_plan, keyword_plan
from app.pipeline.validation import build_look
from app.schemas import ComposedItem, ComposedLook, InspirationAnalysis, StylePreferences
from tests.conftest import FakeAI

CAMEL = SAMPLE_INSPIRATION_INDEX["insp_camel_work"]["analysis"]


def run(ai, wardrobe, analysis=CAMEL, prefs=None, settings=None):
    return run_pipeline(
        ai=ai,
        settings=settings or Settings(ai_backend="off"),
        retriever=NoOpFashionKnowledgeRetriever(),
        wardrobe=wardrobe,
        analysis=analysis,
        prefs=prefs or StylePreferences(),
        inspiration_id="in_1",
        inspiration_image_url="/x",
    )


GOOD = {
    "looks": [
        {
            "strategy": "closest",
            "title": "Camel classic",
            "items": [
                {
                    "garment_id": "s_camel_blazer",
                    "replaces_slot_id": "outerwear-1",
                    "explanation": "Same camel blazer.",
                    "preserved": ["relaxed shoulders"],
                    "changed": [],
                },
                {"garment_id": "s_white_tee", "replaces_slot_id": "top-1", "explanation": "Clean base."},
                {"garment_id": "s_black_trousers", "replaces_slot_id": "bottom-1", "explanation": "Straight leg."},
                {"garment_id": "s_brown_loafers", "replaces_slot_id": "shoes-1", "explanation": "Polished."},
            ],
            "gaps": [],
            "why_it_works": ["Balanced proportions"],
        },
        {
            "strategy": "creative",
            "title": "Sage remix",
            "items": [
                {
                    "garment_id": "s_sage_blazer",
                    "replaces_slot_id": "outerwear-1",
                    "explanation": "Sage instead of camel.",
                },
                {"garment_id": "FAKE_ID_123", "replaces_slot_id": "top-1", "explanation": "Invented!"},
                {"garment_id": "s_ecru_trousers", "replaces_slot_id": "bottom-1", "explanation": "Wide leg."},
            ],
            "gaps": [],
            "why_it_works": [],
        },
    ]
}


async def test_gemini_composition_is_validated(wardrobe):
    gen = await run(FakeAI({"CompositionResult": GOOD}), wardrobe)
    assert gen.engine == "gemini" and gen.engine_note is None
    assert len(gen.looks) == 2
    creative = gen.looks[1]
    assert "FAKE_ID_123" not in [i.garment_id for i in creative.items]
    assert "top-1" in {g.slot_id for g in creative.gaps}
    for lk in gen.looks:
        assert all(i.garment_id in wardrobe for i in lk.items)


async def test_ai_failure_falls_back_to_labelled_rules(wardrobe):
    ai = FakeAI(
        {"CompositionResult": AIError("ai_timeout", "The AI stylist took too long to respond.", retryable=True)}
    )
    gen = await run(ai, wardrobe)
    assert gen.engine == "rules"
    assert "rule-based" in gen.engine_note
    assert gen.looks


async def test_ai_failure_without_fallback_is_an_error(wardrobe):
    ai = FakeAI({"CompositionResult": AIError("ai_timeout", "slow", retryable=True)})
    with pytest.raises(ApiError) as exc:
        await run(ai, wardrobe, settings=Settings(ai_backend="off", composer_fallback="none"))
    assert exc.value.status == 503 and exc.value.retryable


async def test_all_invalid_ids_triggers_fallback(wardrobe):
    bad = {
        "looks": [
            {
                "strategy": "closest",
                "title": "x",
                "items": [{"garment_id": "nope", "replaces_slot_id": "top-1", "explanation": "x"}],
            }
        ]
    }
    gen = await run(FakeAI({"CompositionResult": bad}), wardrobe)
    assert gen.engine == "rules" and gen.looks


async def test_demo_mode_is_labelled(wardrobe):
    gen = await run(None, wardrobe)
    assert gen.engine == "rules" and "Demo mode" in gen.engine_note


async def test_empty_wardrobe_is_409():
    with pytest.raises(ApiError) as exc:
        await run(None, {})
    assert exc.value.status == 409


async def test_non_outfit_image_returns_no_looks(wardrobe):
    not_outfit = InspirationAnalysis(is_outfit=False, summary="A landscape.", formality="casual", pieces=[])
    gen = await run(None, wardrobe, analysis=not_outfit)
    assert gen.looks == [] and gen.no_match_reason


async def test_unowned_keep_ids_are_ignored(wardrobe):
    gen = await run(None, wardrobe, prefs=StylePreferences(keep_garment_ids=["someone_elses"]))
    assert gen.preferences.keep_garment_ids == []


def test_keyword_refinement_keep_and_change(wardrobe):
    look = build_look(
        ComposedLook(
            strategy="closest",
            title="t",
            items=[
                ComposedItem(garment_id="s_camel_blazer", replaces_slot_id="outerwear-1", explanation="x"),
                ComposedItem(garment_id="s_black_trousers", replaces_slot_id="bottom-1", explanation="x"),
            ],
        ),
        wardrobe,
        CAMEL,
        StylePreferences(),
    )
    plan = keyword_plan("Keep the blazer, but change the trousers", look)
    assert plan.keep_garment_ids == ["s_camel_blazer"]
    assert plan.exclude_garment_ids == ["s_black_trousers"]
    prefs = apply_plan(StylePreferences(), plan, wardrobe)
    assert prefs.exclude_garment_ids == ["s_black_trousers"]

    assert keyword_plan("make this more formal", look).occasion == "work"
    assert keyword_plan("give me a more colourful option", look).fidelity == "creative"
    assert keyword_plan("only use items I already own", look).shopping == "wardrobe_first"

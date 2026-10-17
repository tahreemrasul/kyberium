"""Stylist–critic workflow tests. The ADK graph runs for real; Gemini is replaced by a scripted fake."""

import json
from collections.abc import AsyncGenerator

import pytest
from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types

from app.config import Settings
from app.demo import SAMPLE_INSPIRATION_INDEX
from app.knowledge import NoOpFashionKnowledgeRetriever
from app.pipeline.orchestrator import run_pipeline
from app.pipeline.retrieval import rank_candidates
from app.schemas import StylePreferences
from app.stylist.workflow import AgenticError, StylingRun
from tests.conftest import FakeAI

CAMEL = SAMPLE_INSPIRATION_INDEX["insp_camel_work"]["analysis"]


class ScriptedLlm(BaseLlm):
    """Answers the stylist and critic from scripted queues; records every request."""

    model: str = "scripted"
    stylist: list = []
    critic: list = []
    requests: list = []

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        system = str(llm_request.config.system_instruction or "")
        role = "critic" if "REVIEW PACKET" in system else "stylist"
        self.requests.append((role, llm_request))
        queue = self.critic if role == "critic" else self.stylist
        payload = queue.pop(0)
        yield LlmResponse(content=types.Content(role="model", parts=[types.Part(text=json.dumps(payload))]))


def look(strategy, title, items):
    return {
        "strategy": strategy,
        "title": title,
        "items": [{"garment_id": g, "replaces_slot_id": s, "role": "piece", "explanation": "works"} for g, s in items],
        "coherence": "Holds together.",
        "styling_instructions": ["Tuck the tee loosely at the front."],
        "preserved_traits": ["straight, elongated leg line"],
        "deviations": [],
    }


CLASSIC = look(
    "closest",
    "Camel classic",
    [
        ("s_camel_blazer", "outerwear-1"),
        ("s_white_tee", "top-1"),
        ("s_black_trousers", "bottom-1"),
        ("s_brown_loafers", "shoes-1"),
    ],
)
SAGE = look(
    "creative",
    "Sage remix",
    [
        ("s_sage_blazer", "outerwear-1"),
        ("s_breton_tee", "top-1"),
        ("s_ecru_trousers", "bottom-1"),
        ("s_black_boots", "shoes-1"),
    ],
)
SAGE_FIXED = look(
    "creative",
    "Sage, simplified",
    [
        ("s_sage_blazer", "outerwear-1"),
        ("s_white_tee", "top-1"),
        ("s_ecru_trousers", "bottom-1"),
        ("s_brown_loafers", "shoes-1"),
    ],
)


def verdict(i, v, severity=None, problem="", fix=None):
    issues = (
        [{"criterion": "coherence", "severity": severity, "problem": problem, "suggested_fix": fix}] if severity else []
    )
    return {"look_index": i, "verdict": v, "strengths": ["balanced proportions"], "issues": issues}


def make_run(wardrobe, llm, **settings) -> StylingRun:
    prefs = StylePreferences(occasion="work")
    s = Settings(ai_backend="vertex", google_cloud_project="test", **settings)
    return StylingRun(
        settings=s,
        analysis=CAMEL,
        prefs=prefs,
        wardrobe=wardrobe,
        candidates=rank_candidates(CAMEL, list(wardrobe.values()), prefs),
        knowledge=[],
        inspiration_image_url="/media/samples/inspirations/insp_camel_work.png",
        model_override=llm,
    )


async def test_critic_feedback_drives_one_revision(wardrobe):
    llm = ScriptedLlm(
        stylist=[{"looks": [CLASSIC, SAGE]}, {"looks": [SAGE_FIXED]}],
        critic=[
            {
                "evaluations": [
                    verdict(0, "approve"),
                    verdict(
                        1,
                        "revise",
                        "major",
                        "Stripes and boots fight the minimal mood.",
                        "Use the white tee and loafers.",
                    ),
                ],
                "summary": "One fix needed.",
            },
            {"evaluations": [verdict(0, "approve")], "summary": "Fixed."},
        ],
    )
    result = await make_run(wardrobe, llm, max_refinement_rounds=1).run()
    assert [lk.title for lk in result.looks] == ["Camel classic", "Sage, simplified"]
    assert all(lk.review and lk.review.verdict == "approve" for lk in result.looks)
    assert result.looks[1].review.rounds == 1
    assert result.trace.rounds == 2
    assert [s.step for s in result.trace.steps] == ["stylist", "critic", "stylist", "critic"]
    # The revision request carried the critic's concrete fix to the stylist.
    second_stylist = [r for role, r in llm.requests if role == "stylist"][1]
    assert "Use the white tee and loafers." in str(second_stylist.config.system_instruction)


async def test_rejected_looks_are_never_returned(wardrobe):
    bad = {"evaluations": [verdict(0, "reject", "critical", "Incoherent.", "Start over.")], "summary": "No."}
    llm = ScriptedLlm(stylist=[{"looks": [SAGE]}, {"looks": [SAGE_FIXED]}], critic=[bad, bad])
    result = await make_run(wardrobe, llm, max_refinement_rounds=1).run()
    assert result.looks == []
    assert result.no_match_reason and "Incoherent" in result.no_match_reason
    assert result.trace.final_decision == "No look passed the critic"


async def test_loop_is_bounded(wardrobe):
    bad = {"evaluations": [verdict(0, "revise", "major", "Still off.", "Try again.")], "summary": "No."}
    llm = ScriptedLlm(stylist=[{"looks": [SAGE]}] * 3, critic=[bad] * 3)
    result = await make_run(wardrobe, llm, max_refinement_rounds=2).run()
    assert result.trace.rounds == 3 and result.looks == []
    assert len([r for r in llm.requests if r[0] == "stylist"]) == 3


async def test_critic_can_be_disabled(wardrobe):
    llm = ScriptedLlm(stylist=[{"looks": [CLASSIC, SAGE]}], critic=[])
    result = await make_run(wardrobe, llm, critic_enabled=False).run()
    assert len(result.looks) == 2 and all(lk.review is None for lk in result.looks)
    assert [s.step for s in result.trace.steps] == ["stylist"]


async def test_invalid_proposal_triggers_revision_not_critic(wardrobe):
    hallucinated = look("closest", "Imaginary", [("g_not_owned", "outerwear-1"), ("g_also_fake", "top-1")])
    llm = ScriptedLlm(
        stylist=[{"looks": [hallucinated]}, {"looks": [CLASSIC]}],
        critic=[{"evaluations": [verdict(0, "approve")], "summary": "Good."}],
    )
    result = await make_run(wardrobe, llm, max_refinement_rounds=1).run()
    assert [lk.title for lk in result.looks] == ["Camel classic"]
    assert len([r for r in llm.requests if r[0] == "critic"]) == 1
    assert all(i.garment_id in wardrobe for lk in result.looks for i in lk.items)


async def test_minor_only_revise_counts_as_approval(wardrobe):
    llm = ScriptedLlm(
        stylist=[{"looks": [CLASSIC]}],
        critic=[{"evaluations": [verdict(0, "revise", "minor", "Could add a belt.")], "summary": "Nearly."}],
    )
    result = await make_run(wardrobe, llm, max_refinement_rounds=1).run()
    assert len(result.looks) == 1 and result.looks[0].review.notes == ["Could add a belt."]


async def test_unfixable_fidelity_gap_does_not_block(wardrobe):
    unfixable = {
        "criterion": "fidelity",
        "severity": "major",
        "problem": "No white shirt is owned.",
        "suggested_fix": None,
        "fixable_with_wardrobe": False,
    }
    llm = ScriptedLlm(
        stylist=[{"looks": [CLASSIC]}],
        critic=[
            {
                "evaluations": [{"look_index": 0, "verdict": "revise", "strengths": [], "issues": [unfixable]}],
                "summary": "Best available.",
            }
        ],
    )
    result = await make_run(wardrobe, llm, max_refinement_rounds=1).run()
    assert len(result.looks) == 1 and result.looks[0].review.notes == ["No white shirt is owned."]
    assert len([r for r in llm.requests if r[0] == "stylist"]) == 1  # no pointless revision


async def test_critic_sees_garment_images(wardrobe):
    llm = ScriptedLlm(
        stylist=[{"looks": [CLASSIC]}], critic=[{"evaluations": [verdict(0, "approve")], "summary": "ok"}]
    )
    run = make_run(wardrobe, llm)

    async def loader(url):
        return (b"\xff\xd8fake", "image/jpeg")

    run.image_loader = loader
    await run.run()
    critic_req = next(r for role, r in llm.requests if role == "critic")
    images = [p for c in critic_req.contents for p in (c.parts or []) if p.inline_data]
    assert len(images) == 1 + len(CLASSIC["items"])  # inspiration + every garment


async def test_orchestrator_falls_back_when_workflow_fails(wardrobe):
    async def broken(**_):
        raise AgenticError("model unavailable")

    gen = await run_pipeline(
        ai=FakeAI({"CompositionResult": {"looks": [CLASSIC]}}),
        settings=Settings(ai_backend="vertex", google_cloud_project="test"),
        retriever=NoOpFashionKnowledgeRetriever(),
        wardrobe=wardrobe,
        analysis=CAMEL,
        prefs=StylePreferences(occasion="work"),
        inspiration_id="in_1",
        inspiration_image_url="/x",
        agentic_runner=broken,
    )
    assert gen.engine == "gemini" and "without critic review" in gen.engine_note and gen.looks


@pytest.mark.parametrize("engine", ["single_pass"])
async def test_single_pass_engine_flag_skips_workflow(wardrobe, engine):
    async def should_not_run(**_):
        raise AssertionError("agentic runner must not be called")

    gen = await run_pipeline(
        ai=FakeAI({"CompositionResult": {"looks": [CLASSIC]}}),
        settings=Settings(ai_backend="vertex", google_cloud_project="test", styling_engine=engine),
        retriever=NoOpFashionKnowledgeRetriever(),
        wardrobe=wardrobe,
        analysis=CAMEL,
        prefs=StylePreferences(occasion="work"),
        inspiration_id="in_1",
        inspiration_image_url="/x",
        agentic_runner=should_not_run,
    )
    assert gen.engine == "gemini" and gen.trace is None

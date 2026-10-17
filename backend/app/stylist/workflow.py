"""Agentic styling workflow on Google ADK (graph Workflow).

    START → stylist (LlmAgent) → validate ──critique──► critic (LlmAgent) → decide ──done──► finalize
                ▲                    │  └──done──────────────────────────────────────────────► finalize
                └────── revise ──────┴──────────────────────── revise ◄──────────┘

* The stylist composes complete outfits from the OutfitDNA and annotated owned candidates.
* validate reuses the deterministic validation layer (owned ids, caps, occasion, keep/exclude).
* The critic sees the inspiration and garment images and returns structured verdicts.
* decide approves, or sends targeted critique back to the stylist — at most
  ``max_refinement_rounds`` times. Rejected looks are never returned as matches.

Every step is recorded in a ``StylingTrace`` (and logged) for transparency and demos.
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import dataclass, field
from typing import Any

from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.planners import BuiltInPlanner
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.workflow import START, RetryConfig, Workflow, node
from google.genai import types

from app.config import Settings
from app.knowledge import FashionKnowledgeHit
from app.pipeline.validation import build_looks
from app.schemas import (
    CandidateMatch,
    CompositionResult,
    CriticReport,
    Garment,
    InspirationAnalysis,
    Look,
    LookReview,
    StylePreferences,
    StylingTrace,
    TraceStep,
)
from app.stylist.images import ImageLoader
from app.stylist.prompts import CRITIC_SYSTEM, REVISION_PREAMBLE, STYLIST_SYSTEM

log = logging.getLogger("rewear.stylist")
MAX_LOOKS = 3
_STRATEGY_ORDER = {"closest": 0, "creative": 1, "alternative": 2}


class AgenticError(Exception):
    """The workflow could not produce a result (model/transport failure, timeout)."""


@dataclass
class AgenticResult:
    looks: list[Look]
    no_match_reason: str | None
    trace: StylingTrace


def configure_vertex(settings: Settings) -> None:
    """ADK's Gemini model reads Vertex settings from the environment."""
    os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "TRUE")
    if settings.google_cloud_project:
        os.environ.setdefault("GOOGLE_CLOUD_PROJECT", settings.google_cloud_project)
    os.environ.setdefault("GOOGLE_CLOUD_LOCATION", settings.google_cloud_location)


def garment_brief(g: Garment) -> dict:
    return {
        "id": g.id,
        "name": g.name,
        "category": g.category,
        "subcategory": g.subcategory,
        "colors": g.colors,
        "silhouette": g.silhouette,
        "pattern": g.pattern,
        "material_appearance": g.material_appearance,
        "formality": g.formality,
        "layer": g.layer,
        "style_tags": g.style_tags,
    }


def look_brief(look: Look) -> dict:
    return {
        "title": look.title,
        "strategy": look.strategy,
        "items": [
            {"garment_id": i.garment_id, "name": i.garment.name, "replaces": i.replaces_description, "role": i.role}
            for i in look.items
        ],
        "styling_instructions": look.styling_instructions,
    }


@dataclass
class StylingRun:
    settings: Settings
    analysis: InspirationAnalysis
    prefs: StylePreferences
    wardrobe: dict[str, Garment]
    candidates: dict[str, list[CandidateMatch]]
    knowledge: list[FashionKnowledgeHit]
    inspiration_image_url: str
    image_loader: ImageLoader | None = None
    model_override: Any = None  # a BaseLlm instance, used by tests to run the graph offline
    steps: list[TraceStep] = field(default_factory=list)
    round: int = 0
    _t0: dict[str, float] = field(default_factory=dict)

    # ------------------------------------------------------------------ prompts

    @property
    def max_passes(self) -> int:
        return 1 + max(0, self.settings.max_refinement_rounds)

    def brief(self) -> dict:
        shortlisted = {c.garment_id for cs in self.candidates.values() for c in cs}
        return {
            "outfit_dna": self.analysis.model_dump(exclude_none=True),
            "preferences": self.prefs.model_dump(),
            "candidates_per_slot": {
                slot: [
                    {
                        **garment_brief(self.wardrobe[c.garment_id]),
                        "rank_score": c.score,
                        "matching_attributes": c.matching_attributes,
                        "differences": c.differences,
                        "styling_considerations": c.styling_considerations,
                    }
                    for c in cs
                    if c.garment_id in self.wardrobe
                ]
                for slot, cs in self.candidates.items()
            },
            "other_owned_garments": [garment_brief(g) for gid, g in self.wardrobe.items() if gid not in shortlisted][
                :40
            ],
            "owned_garment_ids": sorted(self.wardrobe),
            "styling_principles": [{"id": k.id, "text": k.text} for k in self.knowledge],
            "note": "rank_score is a heuristic ranking value, not a probability.",
        }

    def stylist_instruction(self, ctx) -> str:
        text = STYLIST_SYSTEM + "\n\nREQUEST DATA (JSON):\n" + json.dumps(self.brief())
        revision = ctx.state.get("revision_brief") or ""
        if revision:
            text += "\n\n" + revision
        return text

    def critic_instruction(self, ctx) -> str:
        pending = [Look.model_validate(d) for d in ctx.state.get("pending", [])]
        packet = {
            "outfit_dna": self.analysis.model_dump(exclude_none=True),
            "preferences": self.prefs.model_dump(),
            "looks_under_review": [
                {
                    "look_index": i,
                    "title": lk.title,
                    "strategy": lk.strategy,
                    "items": [
                        {**garment_brief(it.garment), "replaces": it.replaces_description, "role": it.role}
                        for it in lk.items
                    ],
                    "coherence_claim": lk.coherence,
                    "styling_instructions": lk.styling_instructions,
                    "claimed_preserved_traits": lk.preserved_traits,
                    "declared_deviations": lk.deviations,
                    "gaps": [g.description for g in lk.gaps],
                }
                for i, lk in enumerate(pending)
            ],
            "styling_principles": [k.text for k in self.knowledge],
            "owned_wardrobe": [
                {
                    "id": g.id,
                    "name": g.name,
                    "category": g.category,
                    "colors": g.colors,
                    "material_appearance": g.material_appearance,
                }
                for g in self.wardrobe.values()
            ][:60],
        }
        return CRITIC_SYSTEM + "\n\nREVIEW PACKET (JSON):\n" + json.dumps(packet)

    # ------------------------------------------------------------- callbacks

    def _before_stylist(self, callback_context, llm_request):
        self._t0["stylist"] = time.perf_counter()
        return None

    def _after(self, name: str):
        def cb(callback_context, llm_response):
            started = self._t0.pop(name, None)
            usage = getattr(llm_response, "usage_metadata", None)
            tokens = getattr(usage, "total_token_count", None) if usage else None
            latency = int((time.perf_counter() - started) * 1000) if started else None
            self.steps.append(
                TraceStep(
                    step=f"{name}_model_call",
                    round=self.round + (1 if name == "stylist" else 0),
                    summary=f"{name} responded",
                    latency_ms=latency,
                    tokens=tokens,
                )
            )
            return None

        return cb

    async def _attach_images(self, callback_context, llm_request):
        """Give the critic the actual garment and inspiration images."""
        self._t0["critic"] = time.perf_counter()
        if not (self.settings.critic_uses_images and self.image_loader):
            return None
        parts: list[types.Part] = []
        insp = await self.image_loader(self.inspiration_image_url)
        if insp:
            parts += [types.Part(text="INSPIRATION IMAGE:"), types.Part.from_bytes(data=insp[0], mime_type=insp[1])]
        seen: set[str] = set()
        for d in callback_context.state.get("pending", []):
            for it in d.get("items", []):
                g = it["garment"]
                if g["id"] in seen:
                    continue
                seen.add(g["id"])
                img = await self.image_loader(g["image_url"])
                if img:
                    parts += [
                        types.Part(text=f"GARMENT {g['id']} — {g['name']}:"),
                        types.Part.from_bytes(data=img[0], mime_type=img[1]),
                    ]
        if parts:
            llm_request.contents.append(types.Content(role="user", parts=parts))
        return None

    # ------------------------------------------------------------------ nodes

    @staticmethod
    def _looks(state, key: str) -> list[Look]:
        return [Look.model_validate(d) for d in state.get(key, [])]

    def _revision_brief(self, accepted: list[Look], to_fix: list[tuple[Look, list[str]]], note: str = "") -> str:
        lines = [REVISION_PREAMBLE.format(round=self.round, max_looks=max(1, MAX_LOOKS - len(accepted)))]
        if note:
            lines.append(note)
        if accepted:
            lines.append("APPROVED LOOKS (keep, don't duplicate): " + json.dumps([look_brief(a) for a in accepted]))
        for look, issues in to_fix:
            lines.append("LOOK TO FIX: " + json.dumps(look_brief(look)) + "\nCRITIC ISSUES:\n- " + "\n- ".join(issues))
        return "\n\n".join(lines)

    def on_validate(self, state) -> Event:
        """Deterministic validation of the stylist's proposal; routes to critique/revise/done."""
        self.round += 1
        accepted = self._looks(state, "accepted")
        try:
            proposal = CompositionResult.model_validate(state.get("proposal") or {"looks": []})
        except Exception as exc:  # schema drift: treat as an empty proposal
            log.warning("unparseable stylist proposal: %s", exc)
            proposal = CompositionResult(looks=[])
        taken = {frozenset(i.garment_id for i in a.items) for a in accepted}
        looks = build_looks(proposal.looks, self.wardrobe, self.analysis, self.prefs, limit=MAX_LOOKS)
        fresh = [lk for lk in looks if frozenset(i.garment_id for i in lk.items) not in taken]
        removed = len(proposal.looks) - len(fresh)
        details = [f"{lk.title}: " + ", ".join(i.garment.name for i in lk.items) for lk in fresh]
        details += [w for lk in fresh for w in lk.warnings]
        self.steps.append(
            TraceStep(
                step="stylist",
                round=self.round,
                summary=f"Stylist proposed {len(proposal.looks)} look(s); {len(fresh)} passed validation"
                + (f", {removed} removed (invalid or duplicate)" if removed else ""),
                details=details[:8],
            )
        )
        delta: dict = {"pending": [lk.model_dump(mode="json") for lk in fresh], "no_match": proposal.no_match_reason}
        if not fresh:
            if self.round < self.max_passes and proposal.looks:
                note = "Your previous proposals were removed by validation (unowned ids, duplicates or broken rules)."
                delta["revision_brief"] = self._revision_brief(accepted, [], note)
                return Event(output="revise", route="revise", state=delta)
            return Event(output="done", route="done", state=delta)
        if not self.settings.critic_enabled:
            delta["accepted"] = [lk.model_dump(mode="json") for lk in accepted + fresh]
            return Event(output="done", route="done", state=delta)
        return Event(output="critique", route="critique", state=delta)

    def on_decide(self, state) -> Event:
        """Apply the critic's verdicts; approve, or send targeted feedback back to the stylist."""
        accepted = self._looks(state, "accepted")
        pending = self._looks(state, "pending")
        try:
            report = CriticReport.model_validate(state.get("critique") or {})
        except Exception as exc:
            log.warning("unparseable critic report: %s", exc)
            report = CriticReport(evaluations=[], summary="The critic's review could not be read.")
        evals = {e.look_index: e for e in report.evaluations}
        to_fix: list[tuple[Look, list[str]]] = []
        details: list[str] = []
        for i, look in enumerate(pending):
            ev = evals.get(i)
            if ev is None:
                to_fix.append((look, ["The critic did not review this look."]))
                details.append(f"{look.title}: not reviewed")
                continue
            # Only actionable problems block a look: revising can't fix what the wardrobe can't supply.
            # Unfixable incoherence or occasion mismatch still blocks; unfixable fidelity gaps become notes.
            blocking = [
                x
                for x in ev.issues
                if x.fixable_with_wardrobe
                or (x.severity == "critical" and x.criterion in ("coherence", "occasion", "compatibility"))
            ]
            serious = [x for x in blocking if x.severity in ("major", "critical")]
            critical = [x for x in blocking if x.severity == "critical"]
            # Consistency guard: verdict and issue severities must agree.
            approved = (ev.verdict == "approve" and not critical) or (ev.verdict == "revise" and not serious)
            if approved and len(accepted) < MAX_LOOKS:
                look.review = LookReview(
                    verdict="approve",
                    strengths=ev.strengths[:4],
                    notes=[x.problem for x in ev.issues][:3],
                    rounds=self.round - 1,
                )
                accepted.append(look)
                details.append(f"✓ {look.title}: approved" + (f" — {ev.strengths[0]}" if ev.strengths else ""))
            else:
                issues = [
                    f"[{x.severity}] {x.criterion}: {x.problem}"
                    + (f" Fix: {x.suggested_fix}" if x.suggested_fix else "")
                    for x in (serious or ev.issues)
                ] or [f"verdict {ev.verdict}"]
                to_fix.append((look, issues))
                details.append(f"✗ {look.title}: {ev.verdict} — {issues[0]}")
        can_revise = bool(to_fix) and self.round < self.max_passes and len(accepted) < MAX_LOOKS
        self.steps.append(
            TraceStep(
                step="critic",
                round=self.round,
                summary=f"Critic approved {len(pending) - len(to_fix)} of {len(pending)}"
                + ("; sending feedback to the stylist" if can_revise else ""),
                details=(details + ([report.summary] if report.summary else []))[:8],
            )
        )
        delta: dict = {"accepted": [lk.model_dump(mode="json") for lk in accepted], "critic_summary": report.summary}
        if can_revise:
            delta["revision_brief"] = self._revision_brief(accepted, to_fix)
            return Event(output="revise", route="revise", state=delta)
        if to_fix:
            delta["dropped"] = [f"{lk.title}: {issues[0]}" for lk, issues in to_fix]
        return Event(output="done", route="done", state=delta)

    def build(self) -> Workflow:
        s = self.settings
        stylist = LlmAgent(
            name="stylist",
            model=self.model_override or s.composer_model,
            instruction=self.stylist_instruction,
            include_contents="none",
            output_schema=CompositionResult,
            output_key="proposal",
            planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(thinking_budget=s.stylist_thinking_budget)),
            generate_content_config=types.GenerateContentConfig(temperature=0.7),
            before_model_callback=self._before_stylist,
            after_model_callback=self._after("stylist"),
        )
        critic = LlmAgent(
            name="critic",
            model=self.model_override or s.gemini_model,
            instruction=self.critic_instruction,
            include_contents="none",
            output_schema=CriticReport,
            output_key="critique",
            planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(thinking_budget=s.critic_thinking_budget)),
            generate_content_config=types.GenerateContentConfig(temperature=0.2),
            before_model_callback=self._attach_images,
            after_model_callback=self._after("critic"),
        )
        retry = RetryConfig(max_attempts=3, initial_delay=2.0, backoff_factor=2.0, max_delay=10.0)
        stylist_node = node(stylist, retry_config=retry)
        critic_node = node(critic, retry_config=retry)

        @node(name="validate")
        async def validate(ctx):
            return self.on_validate(ctx.state)

        @node(name="decide")
        async def decide(ctx):
            return self.on_decide(ctx.state)

        @node(name="finalize")
        async def finalize(ctx):
            return Event(output={"accepted": len(ctx.state.get("accepted", []))})

        return Workflow(
            name="rewear_styling",
            edges=[
                (START, stylist_node, validate),
                (validate, {"critique": critic_node, "revise": stylist_node, "done": finalize}),
                (critic_node, decide),
                (decide, {"revise": stylist_node, "done": finalize}),
            ],
        )

    # -------------------------------------------------------------------- run

    def result(self, state: dict, started: float) -> AgenticResult:
        accepted = self._looks(state, "accepted")
        accepted.sort(key=lambda lk: _STRATEGY_ORDER.get(lk.strategy, 9))
        used: set[str] = set()
        for lk in accepted:  # keep strategy labels unique for the UI tabs
            if lk.strategy in used:
                lk.strategy = next((x for x in ("creative", "alternative") if x not in used), lk.strategy)
            used.add(lk.strategy)

        no_match = None
        if not accepted:
            no_match = (
                state.get("no_match")
                or state.get("critic_summary")
                or "No convincing outfit could be built from this wardrobe."
            )
            dropped = state.get("dropped") or []
            if dropped:
                no_match += " What didn't work: " + "; ".join(dropped[:2])

        llm_steps = [x for x in self.steps if x.step.endswith("_model_call")]
        steps = [x for x in self.steps if not x.step.endswith("_model_call")]
        for x in llm_steps:  # attach per-call latency/tokens to the matching node step
            target = next((t for t in steps if t.round == x.round and x.step.startswith(t.step)), None)
            if target:
                target.latency_ms = (target.latency_ms or 0) + (x.latency_ms or 0)
                target.tokens = (target.tokens or 0) + (x.tokens or 0)
        trace = StylingTrace(
            engine="adk-workflow",
            rounds=self.round,
            steps=steps,
            total_latency_ms=int((time.perf_counter() - started) * 1000),
            total_tokens=sum(x.tokens or 0 for x in llm_steps) or None,
            final_decision=(
                f"{len(accepted)} look(s) approved after {self.round} stylist pass(es)"
                if accepted
                else "No look passed the critic"
            ),
        )
        log.info("styling trace %s", trace.model_dump_json())
        return AgenticResult(looks=accepted[:MAX_LOOKS], no_match_reason=no_match, trace=trace)

    async def run(self) -> AgenticResult:
        configure_vertex(self.settings)
        started = time.perf_counter()
        sessions = InMemorySessionService()
        runner = Runner(app_name="rewear", node=self.build(), session_service=sessions)
        session = await sessions.create_session(
            app_name="rewear", user_id="stylist", state={"accepted": [], "pending": [], "revision_brief": ""}
        )
        message = types.Content(role="user", parts=[types.Part(text="Style this inspiration from my wardrobe.")])

        async def drive():
            async for _ in runner.run_async(user_id="stylist", session_id=session.id, new_message=message):
                pass

        try:
            await asyncio.wait_for(drive(), timeout=self.settings.agentic_timeout_s)
        except TimeoutError as exc:
            raise AgenticError("the stylist–critic workflow timed out") from exc
        except Exception as exc:
            raise AgenticError(f"the stylist–critic workflow failed: {exc}") from exc

        final = await sessions.get_session(app_name="rewear", user_id="stylist", session_id=session.id)
        return self.result(final.state if final else {}, started)


async def run_agentic(
    *,
    settings: Settings,
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
    wardrobe: dict[str, Garment],
    candidates: dict[str, list[CandidateMatch]],
    knowledge: list[FashionKnowledgeHit],
    inspiration_image_url: str,
    image_loader: ImageLoader | None,
) -> AgenticResult:
    return await StylingRun(
        settings=settings,
        analysis=analysis,
        prefs=prefs,
        wardrobe=wardrobe,
        candidates=candidates,
        knowledge=knowledge,
        inspiration_image_url=inspiration_image_url,
        image_loader=image_loader,
    ).run()

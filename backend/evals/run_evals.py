"""Rewear evaluation runner.

Offline (default): deterministic pipeline (rule-based composer) plus injected model
outputs for the hallucination / malformed cases. Fast, credential-free, run in CI.

Live (--live): uses Gemini on Vertex AI for the composer (sample inspirations keep
their reviewed analyses so results are comparable). Needs GOOGLE_CLOUD_PROJECT and ADC.

    uv run python -m evals.run_evals            # offline
    uv run python -m evals.run_evals --live     # Gemini

Writes evals/results/latest[-live].md. Checks are pass/fail on grounded, objective
properties; subjective quality (explanations, creativity) is reviewed by a human from
the generated report.
"""

import argparse
import asyncio
import io
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from PIL import Image

from app.ai.client import AIError, get_ai
from app.config import Settings, get_settings
from app.demo import SAMPLE_INSPIRATION_INDEX, sample_garments
from app.errors import ApiError
from app.knowledge import get_retriever
from app.pipeline.orchestrator import run_pipeline
from app.schemas import Garment, Generation, InspirationAnalysis, StylePreferences
from app.stylist.images import make_image_loader

HERE = Path(__file__).parent


class InjectedAI:
    """Returns a fixed composer output (or failure) to test validation paths."""

    def __init__(self, output: Any) -> None:
        self.output = output
        self.settings = Settings(ai_backend="vertex", google_cloud_project="eval")

    async def generate_json(self, *, schema, **_: Any):
        if self.output == "__ERROR__":
            raise AIError("ai_malformed_output", "The AI returned an unusable answer.", retryable=True)
        return schema.model_validate(self.output)


REAL_IMAGES = HERE.parent.parent / "images"  # the team's own garment photos (kept out of git)


def real_garments() -> list[Garment]:
    """Garments tagged by Gemini from real photos (evals/fixtures/real_wardrobe.json)."""
    now = datetime.now(UTC)
    out = []
    for rec in json.loads((HERE / "fixtures" / "real_wardrobe.json").read_text()):
        rec = dict(rec)
        image = rec.pop("image_file")
        path = REAL_IMAGES / image if image else None
        out.append(
            Garment(
                **rec,
                image_url=f"file://{path}" if path and path.exists() else "/none",
                image_kind="photo",
                source="upload",
                created_at=now,
                updated_at=now,
            )
        )
    return out


def eval_image_loader():
    """Sample assets via the app loader; real photos straight from disk."""
    base = make_image_loader(None)

    async def load(url: str):
        if url.startswith("file://"):
            path = Path(url.removeprefix("file://"))
            if path.is_file():
                img = Image.open(path).convert("RGB")
                img.thumbnail((384, 384))
                buf = io.BytesIO()
                img.save(buf, format="JPEG", quality=82)
                return buf.getvalue(), "image/jpeg"
            return None
        return await base(url)

    return load


def build_wardrobe(spec: dict | None) -> dict:
    spec = spec or {}
    items = real_garments() if spec.get("fixture") == "real" else sample_garments()
    if "only_categories" in spec:
        items = [g for g in items if g.category in spec["only_categories"]]
    if "exclude_layers" in spec:
        items = [g for g in items if g.layer not in spec["exclude_layers"]]
    if "exclude" in spec:
        items = [g for g in items if g.id not in spec["exclude"]]
    return {g.id: g for g in items}


def load_analysis(value: str | dict) -> InspirationAnalysis:
    if isinstance(value, str):
        return SAMPLE_INSPIRATION_INDEX[value]["analysis"]
    return InspirationAnalysis.model_validate(value)


def check(case: dict, gen: Generation | None, error: ApiError | None, wardrobe: dict) -> list[tuple[str, bool]]:
    exp = case["expect"]
    if "error_status" in exp:
        return [("expected error status", error is not None and error.status == exp["error_status"])]
    if error is not None or gen is None:
        return [("pipeline succeeded", False)]

    looks = gen.looks
    closest = looks[0] if looks else None
    owned_ids = [i.garment_id for lk in looks for i in lk.items]
    slots = {p.slot_id for p in gen.analysis.pieces}
    results: list[tuple[str, bool]] = [
        ("schema valid", Generation.model_validate(gen.model_dump()) is not None),
        ("all garment ids owned", all(g in wardrobe for g in owned_ids)),
        (
            "every slot covered or listed as gap",
            all({i.replaces_slot_id for i in lk.items} | {g.slot_id for g in lk.gaps} >= slots for lk in looks),
        ),
    ]

    def slot_map(lk):
        return {i.replaces_slot_id: i.garment_id for i in lk.items}

    if "min_looks" in exp:
        results.append((f">={exp['min_looks']} looks", len(looks) >= exp["min_looks"]))
    if exp.get("no_looks"):
        results.append(("no looks + reason", not looks and bool(gen.no_match_reason)))
    if "closest_slots" in exp and closest:
        sm = slot_map(closest)
        results += [(f"{slot} -> {gid}", sm.get(slot) == gid) for slot, gid in exp["closest_slots"].items()]
    if "closest_slot_in" in exp and closest:
        sm = slot_map(closest)
        results += [
            (f"{slot} in {allowed}", sm.get(slot) in allowed) for slot, allowed in exp["closest_slot_in"].items()
        ]
    if "covered_slots" in exp and closest:
        results.append(("key slots covered", set(exp["covered_slots"]) <= {i.replaces_slot_id for i in closest.items}))
    for slot, cats in exp.get("slot_covered_by_categories", {}).items():
        ok = any({i.garment.category for i in lk.items if i.replaces_slot_id == slot} >= set(cats) for lk in looks)
        results.append((f"{slot} covered by {cats}", ok))
    if exp.get("no_purchase") and closest:
        results.append(("no purchase needed", not closest.impact.purchase_needed))
    if exp.get("purchase_needed") and closest:
        results.append(("purchase needed flagged", closest.impact.purchase_needed))
    if "max_gaps" in exp and closest:
        results.append((f"<={exp['max_gaps']} gaps", len(closest.gaps) <= exp["max_gaps"]))
    if closest:
        gaps = {g.slot_id: g for g in closest.gaps}
        results += [(f"{s} optional gap", s in gaps and not gaps[s].essential) for s in exp.get("optional_gaps", [])]
        results += [(f"{s} essential gap", s in gaps and gaps[s].essential) for s in exp.get("essential_gaps", [])]
        if "gap_slots" in exp:
            results.append(("expected gap slots", set(exp["gap_slots"]) <= set(gaps)))
        if exp.get("sourcing_hint_on_gaps"):
            results.append(("gaps carry sourcing hints", all(g.sourcing_hint for g in closest.gaps)))
    if exp.get("no_sourcing_hints"):
        results.append(("no sourcing hints", all(not g.sourcing_hint for lk in looks for g in lk.gaps)))
    if "forbidden_garments" in exp:
        results.append(("forbidden garments absent", not set(exp["forbidden_garments"]) & set(owned_ids)))
    if "required_garments" in exp:
        req = set(exp["required_garments"])
        results.append(
            (
                "required garments in every look",
                bool(looks) and all(req <= {i.garment_id for i in lk.items} for lk in looks),
            )
        )
    if "distinct_looks" in exp:
        sets = {frozenset(i.garment_id for i in lk.items) for lk in looks}
        results.append((f"{exp['distinct_looks']} distinct looks", len(sets) >= exp["distinct_looks"]))
    if "engine" in exp:
        results.append((f"engine={exp['engine']}", gen.engine == exp["engine"]))
    if exp.get("honest_gap_or_none"):
        honest = (not looks) or all(lk.gaps or lk.deviations or lk.impact.purchase_needed for lk in looks)
        results.append(("honest about what can't be recreated", honest))
    if "engine_note_contains" in exp:
        results.append(("engine labelled", exp["engine_note_contains"] in (gen.engine_note or "")))
    return results


async def run_case(case: dict, live: bool) -> dict:
    wardrobe = build_wardrobe(case.get("wardrobe"))
    analysis = load_analysis(case["inspiration"])
    prefs = StylePreferences(**case.get("preferences", {}))
    ai = InjectedAI(case["composer_output"]) if "composer_output" in case else (get_ai() if live else None)
    settings = get_settings() if live else Settings(ai_backend="off")
    started = time.perf_counter()
    gen, error = None, None
    try:
        gen = await run_pipeline(
            ai=ai,
            settings=settings,
            retriever=get_retriever(),
            wardrobe=wardrobe,
            analysis=analysis,
            prefs=prefs,
            inspiration_id="eval",
            inspiration_image_url="/eval",
        )
    except ApiError as exc:
        error = exc
    checks = check(case, gen, error, wardrobe)
    return {
        "case": case,
        "checks": checks,
        "passed": all(ok for _, ok in checks),
        "latency_ms": int((time.perf_counter() - started) * 1000),
        "generation": gen,
    }


def report(results: list[dict], live: bool) -> str:
    passed = sum(r["passed"] for r in results)
    checks = [ok for r in results for _, ok in r["checks"]]
    gens = [r["generation"] for r in results if r["generation"]]
    n_looks = sum(len(g.looks) for g in gens)
    lines = [
        f"# Rewear evaluation — {'live Gemini composer' if live else 'offline (rule-based composer + injected model outputs)'}",
        "",
        f"- Cases passed: **{passed}/{len(results)}**",
        f"- Checks passed: **{sum(checks)}/{len(checks)}**",
        "- Owned-garment validity: every returned garment id is checked per case (target 100%).",
        f"- Looks needing no purchase: {sum(not lk.impact.purchase_needed for g in gens for lk in g.looks)}/{n_looks}"
        " (descriptive, not a target)",
        "",
        "Checks are deterministic. Candidate `score` values are heuristic ranking signals, not calibrated "
        "probabilities, and are never shown to users as confidence.",
        "",
        "| Case | Result | Failed checks | Latency |",
        "|---|---|---|---|",
    ]
    for r in results:
        failed = ", ".join(name for name, ok in r["checks"] if not ok) or "—"
        lines.append(f"| {r['case']['id']} | {'PASS' if r['passed'] else 'FAIL'} | {failed} | {r['latency_ms']} ms |")
    lines += ["", "## Looks for human review", ""]
    for r in results:
        g = r["generation"]
        lines.append(f"### {r['case']['id']}\n\n_{r['case']['description']}_\n")
        if not g:
            lines.append("(no generation — expected error)\n")
            continue
        if g.engine_note:
            lines.append(f"> {g.engine_note}\n")
        if not g.looks:
            lines.append(f"No looks: {g.no_match_reason}\n")
        for lk in g.looks:
            lines.append(f"**{lk.title}** — {lk.impact.headline}\n")
            lines += [f"- {it.replaces_slot_id or 'extra'} <- {it.garment.name}: {it.explanation}" for it in lk.items]
            lines += [
                f"- GAP {gp.slot_id} ({'essential' if gp.essential else 'optional'}): {gp.reason}" for gp in lk.gaps
            ]
            lines.append("")
    return "\n".join(lines)


async def run_all(live: bool = False) -> list[dict]:
    cases = json.loads((HERE / "cases.json").read_text())
    return [await run_case(c, live) for c in cases]


async def main(live: bool) -> int:
    results = await run_all(live)
    out = HERE / "results" / ("latest-live.md" if live else "latest.md")
    out.parent.mkdir(exist_ok=True)
    out.write_text(report(results, live))
    for r in results:
        print(("PASS " if r["passed"] else "FAIL ") + r["case"]["id"], [n for n, ok in r["checks"] if not ok] or "")
    print(f"\n{sum(r['passed'] for r in results)}/{len(results)} cases passed — report: {out}")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="use Gemini via Vertex AI for composition")
    sys.exit(asyncio.run(main(parser.parse_args().live)))

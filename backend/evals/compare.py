"""Engine comparison on live Gemini: baseline single pass vs ADK stylist–critic (and ablations).

    uv run python -m evals.compare                                   # all cases, baseline vs agentic
    uv run python -m evals.compare --only real                       # real-wardrobe cases only
    uv run python -m evals.compare --variants agentic agentic_no_images --only real   # image ablation

Writes evals/results/compare.md (+ compare.json with raw looks/timings):
objective checks, invalid-id counts, per-stage latency, tokens, and every variant's looks side by
side with BLANK human-rating fields. The critic's verdicts are reported separately from human
ratings: they are model judgements, not quality scores.
"""

import argparse
import asyncio
import json
import statistics
import sys
import time

from app.ai.client import get_ai
from app.config import get_settings
from app.errors import ApiError
from app.knowledge import get_retriever
from app.pipeline.orchestrator import run_pipeline
from app.schemas import StylePreferences
from evals.run_evals import HERE, build_wardrobe, check, eval_image_loader, load_analysis

VARIANTS: dict[str, dict] = {
    "single_pass": {"styling_engine": "single_pass"},
    "agentic": {"styling_engine": "agentic"},
    "agentic_no_images": {"styling_engine": "agentic", "critic_uses_images": False},
    "agentic_no_revision": {"styling_engine": "agentic", "max_refinement_rounds": 0},
}
STAGES = [
    "retrieval_ms",
    "knowledge_ms",
    "composer_ms",
    "stylist_ms",
    "critic_image_prep_ms",
    "critic_ms",
    "revision_ms",
    "total_ms",
]
COUNTS = [
    "passes",
    "stylist_calls",
    "critic_calls",
    "critic_images",
    "critic_image_tokens",
    "stylist_tokens",
    "critic_tokens",
]


def load_cases(only: str | None, ids: list[str] | None) -> list[dict]:
    sample = [
        c
        for c in json.loads((HERE / "cases.json").read_text())
        if "composer_output" not in c and "error_status" not in c["expect"]
    ]
    real = json.loads((HERE / "real_cases.json").read_text())
    cases = real if only == "real" else sample if only == "sample" else real + sample
    return [c for c in cases if not ids or c["id"] in ids]


def classify_empty(case: dict, gen) -> str:
    """For runs without looks: is 'no match' the expected honest answer, or likely over-rejection?"""
    exp = case["expect"]
    if exp.get("honest_gap_or_none") or exp.get("no_looks"):
        return "legitimate no-match (expected for this case)"
    steps = gen.trace.steps if gen and gen.trace else []
    proposed = any(
        s.step == "stylist" and "passed validation" in s.summary and " 0 passed" not in s.summary for s in steps
    )
    if proposed:
        return "possible over-rejection (stylist proposed valid looks; critic rejected all)"
    return "stylist declined (no proposal) — review whether a coherent outfit existed"


async def run_one(case: dict, variant: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        settings = get_settings().model_copy(update=VARIANTS[variant])
        wardrobe = build_wardrobe(case.get("wardrobe"))
        analysis = load_analysis(case["inspiration"])
        insp = case["inspiration"]
        image = f"/media/samples/inspirations/{insp}.png" if isinstance(insp, str) else "/none"
        started = time.perf_counter()
        gen, error = None, None
        try:
            gen = await run_pipeline(
                ai=get_ai(),
                settings=settings,
                retriever=get_retriever(),
                wardrobe=wardrobe,
                analysis=analysis,
                prefs=StylePreferences(**case.get("preferences", {})),
                inspiration_id="eval",
                inspiration_image_url=image,
                image_loader=eval_image_loader(),
            )
        except ApiError as exc:
            error = exc
        latency = int((time.perf_counter() - started) * 1000)
        checks = check(case, gen, error, wardrobe)
        ids = [i.garment_id for lk in (gen.looks if gen else []) for i in lk.items]
        trace = gen.trace if gen else None
        passed = all(ok for _, ok in checks)
        print(f"{variant:20} {case['id']:34} {'PASS' if passed else 'FAIL'} {latency} ms", flush=True)
        return {
            "case": case,
            "variant": variant,
            "gen": gen,
            "checks": checks,
            "latency_ms": latency,
            "passed": passed,
            "invalid_ids": [i for i in ids if i not in wardrobe],
            "critic_flags": sum(d.startswith("✗") for s in (trace.steps if trace else []) for d in s.details),
            "actual_engine": gen.engine if gen else "error",
            "timings": dict(gen.timings) if gen else {},
            "empty_reason": classify_empty(case, gen) if gen and not gen.looks else None,
        }


def _median(rows: list[dict], key: str) -> str:
    vals = [r["timings"].get(key) for r in rows if r["timings"].get(key) is not None]
    return f"{int(statistics.median(vals))}" if vals else "–"


def summarise(rows: list[dict], variants: list[str]) -> list[str]:
    out = [
        "| Variant | Objective checks | Invalid owned ids | Looks returned | With styling instructions "
        "| Critic rejections | No-look runs (legit / suspect) | Median total | Max total |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for v in variants:
        rs = [r for r in rows if r["variant"] == v]
        looks = [lk for r in rs if r["gen"] for lk in r["gen"].looks]
        totals = sorted(r["latency_ms"] for r in rs) or [0]
        empties = [r for r in rs if r["empty_reason"]]
        legit = sum(r["empty_reason"].startswith("legitimate") for r in empties)
        out.append(
            f"| {v} | {sum(r['passed'] for r in rs)}/{len(rs)} | {sum(len(r['invalid_ids']) for r in rs)} "
            f"| {len(looks)} | {sum(bool(lk.styling_instructions) for lk in looks)} "
            f"| {sum(r['critic_flags'] for r in rs)} | {legit} / {len(empties) - legit} "
            f"| {totals[len(totals) // 2] / 1000:.1f} s | {totals[-1] / 1000:.1f} s |"
        )
    out += ["", "### Median per-stage latency (ms) and cost counters", ""]
    out.append("| Variant | " + " | ".join(STAGES + COUNTS) + " |")
    out.append("|---|" + "---|" * (len(STAGES) + len(COUNTS)))
    for v in variants:
        rs = [r for r in rows if r["variant"] == v]
        out.append(f"| {v} | " + " | ".join(_median(rs, k) for k in STAGES + COUNTS) + " |")
    out += [
        "",
        "`revision_ms` = model time in passes after the first; `critic_ms` excludes image preparation "
        "(`critic_image_prep_ms`). Values are medians per request.",
    ]
    return out


def render_look(lk) -> list[str]:
    pieces = ", ".join(f"{i.garment.name} → {i.replaces_description or 'extra'}" for i in lk.items)
    lines = [f"- **{lk.title}** ({lk.strategy}) — {lk.impact.headline}", f"  - Pieces: {pieces}"]
    if lk.styling_instructions:
        lines.append("  - How to wear: " + " / ".join(lk.styling_instructions))
    if lk.deviations:
        lines.append("  - Declared deviations: " + "; ".join(lk.deviations))
    if lk.gaps:
        gaps = "; ".join(f"{g.description} ({'essential' if g.essential else 'optional'})" for g in lk.gaps)
        lines.append("  - Gaps: " + gaps)
    if lk.review:
        notes = f"; notes: {'; '.join(lk.review.notes)}" if lk.review.notes else ""
        lines.append(f"  - Gemini critic: approved after {lk.review.rounds} revision(s){notes}")
    return lines


def report(rows: list[dict], variants: list[str]) -> str:
    lines = ["# Rewear — engine comparison (live Gemini)", ""]
    lines += ["Variants: " + ", ".join(f"`{v}` {VARIANTS[v]}" for v in variants), "", "## Summary", ""]
    lines += summarise(rows, variants)
    lines += ["", "## Looks per case (human rating fields are intentionally blank)", ""]
    for case_id in dict.fromkeys(r["case"]["id"] for r in rows):
        group = [r for r in rows if r["case"]["id"] == case_id]
        lines += [f"### {case_id}", "", f"_{group[0]['case']['description']}_", ""]
        for r in group:
            g = r["gen"]
            failed = ", ".join(n for n, ok in r["checks"] if not ok) or "all objective checks pass"
            lines.append(f"**{r['variant']}** · {r['latency_ms'] / 1000:.1f} s · {failed} · human rating: ___/5")
            if not g:
                lines.append("- (error)")
            elif not g.looks:
                lines.append(f"- No looks — {r['empty_reason']}: {g.no_match_reason}")
            for lk in g.looks if g else []:
                lines += render_look(lk)
            if g and g.trace:
                lines.append("- Workflow: " + " → ".join(s.summary for s in g.trace.steps))
            lines.append("")
    return "\n".join(lines)


def dump(rows: list[dict]) -> list[dict]:
    return [
        {
            "case": r["case"]["id"],
            "variant": r["variant"],
            "latency_ms": r["latency_ms"],
            "passed": r["passed"],
            "failed_checks": [n for n, ok in r["checks"] if not ok],
            "timings": r["timings"],
            "empty_reason": r["empty_reason"],
            "generation": r["gen"].model_dump(mode="json") if r["gen"] else None,
        }
        for r in rows
    ]


async def main(only: str | None, ids: list[str] | None, variants: list[str], concurrency: int, out: str) -> int:
    if get_ai() is None:
        print("Live comparison needs Gemini (set GOOGLE_CLOUD_PROJECT and AI_BACKEND=vertex).", file=sys.stderr)
        return 2
    sem = asyncio.Semaphore(concurrency)
    cases = load_cases(only, ids)
    rows = list(await asyncio.gather(*(run_one(c, v, sem) for c in cases for v in variants)))
    results = HERE / "results"
    results.mkdir(exist_ok=True)
    (results / f"{out}.md").write_text(report(rows, variants))
    (results / f"{out}.json").write_text(json.dumps(dump(rows), indent=1))
    print("\n".join(summarise(rows, variants)))
    print(f"\nreport: {results / (out + '.md')}")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=["real", "sample"])
    p.add_argument("--cases", nargs="*")
    p.add_argument("--variants", nargs="*", default=["single_pass", "agentic"], choices=list(VARIANTS))
    p.add_argument("--concurrency", type=int, default=3)
    p.add_argument("--out", default="compare")
    a = p.parse_args()
    sys.exit(asyncio.run(main(a.only, a.cases, a.variants, a.concurrency, a.out)))

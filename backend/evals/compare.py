"""Baseline (single-pass Gemini) vs agentic (ADK stylist–critic) comparison on live Gemini.

    uv run python -m evals.compare                 # all cases (sample + real wardrobe)
    uv run python -m evals.compare --only real     # real-wardrobe cases only

Writes evals/results/compare.md: objective checks, hallucination rate, latency and tokens
per engine, plus both engines' looks side by side for HUMAN rating (blank column). We
deliberately do not auto-score taste: the critic's verdicts are not objective quality.
"""

import argparse
import asyncio
import json
import sys
import time

from app.ai.client import get_ai
from app.config import get_settings
from app.errors import ApiError
from app.knowledge import get_retriever
from app.pipeline.orchestrator import run_pipeline
from app.schemas import StylePreferences
from evals.run_evals import HERE, build_wardrobe, check, eval_image_loader, load_analysis

ENGINES = ("single_pass", "agentic")


def load_cases(only: str | None) -> list[dict]:
    sample = [
        c
        for c in json.loads((HERE / "cases.json").read_text())
        if "composer_output" not in c and "error_status" not in c["expect"]
    ]
    real = json.loads((HERE / "real_cases.json").read_text())
    return real if only == "real" else sample if only == "sample" else real + sample


async def run_one(case: dict, engine: str, sem: asyncio.Semaphore) -> dict:
    async with sem:
        settings = get_settings().model_copy(update={"styling_engine": engine})
        wardrobe = build_wardrobe(case.get("wardrobe"))
        analysis = load_analysis(case["inspiration"])
        image = (
            f"/media/samples/inspirations/{case['inspiration']}.png"
            if isinstance(case["inspiration"], str)
            else "/none"
        )
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
        critic_flags = sum(d.startswith("✗") for s in (trace.steps if trace else []) for d in s.details)
        passed = all(ok for _, ok in checks)
        print(f"{engine:11} {case['id']:34} {'PASS' if passed else 'FAIL'} {latency} ms", flush=True)
        return {
            "case": case,
            "engine": engine,
            "gen": gen,
            "checks": checks,
            "latency_ms": latency,
            "passed": passed,
            "ids": ids,
            "invalid_ids": [i for i in ids if i not in wardrobe],
            "tokens": trace.total_tokens if trace else None,
            "rounds": trace.rounds if trace else 1,
            "critic_flags": critic_flags,
            "actual_engine": gen.engine if gen else "error",
        }


def summarise(rows: list[dict]) -> list[str]:
    out = [
        "| Engine | Cases passed | Invalid owned ids | Looks returned | Looks with styling instructions "
        "| Critic interventions | Median latency | Max latency | Avg tokens* |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for eng in ENGINES:
        rs = [r for r in rows if r["engine"] == eng]
        looks = [lk for r in rs if r["gen"] for lk in r["gen"].looks]
        lat = sorted(r["latency_ms"] for r in rs)
        toks = [r["tokens"] for r in rs if r["tokens"]]
        out.append(
            f"| {eng} | {sum(r['passed'] for r in rs)}/{len(rs)} | {sum(len(r['invalid_ids']) for r in rs)} "
            f"| {len(looks)} | {sum(bool(lk.styling_instructions) for lk in looks)} "
            f"| {sum(r['critic_flags'] for r in rs)} | {lat[len(lat) // 2] if lat else 0} ms "
            f"| {lat[-1] if lat else 0} ms | {int(sum(toks) / len(toks)) if toks else 'n/a'} |"
        )
    out.append("")
    out.append("*Token totals are tracked for the agentic workflow's model calls (single-pass logs them per call).")
    return out


def render_look(lk) -> list[str]:
    lines = [f"- **{lk.title}** ({lk.strategy}) — {lk.impact.headline}"]
    lines.append(
        "  - Pieces: " + ", ".join(f"{i.garment.name} → {i.replaces_description or 'extra'}" for i in lk.items)
    )
    if lk.coherence:
        lines.append(f"  - Coherence: {lk.coherence}")
    if lk.styling_instructions:
        lines.append("  - How to wear: " + " / ".join(lk.styling_instructions))
    if lk.deviations:
        lines.append("  - Declared deviations: " + "; ".join(lk.deviations))
    if lk.gaps:
        gaps = "; ".join(f"{g.description} ({'essential' if g.essential else 'optional'})" for g in lk.gaps)
        lines.append("  - Gaps: " + gaps)
    if lk.review:
        notes = f"; notes: {'; '.join(lk.review.notes)}" if lk.review.notes else ""
        lines.append(f"  - Critic: approved after {lk.review.rounds} revision(s){notes}")
    return lines


def report(rows: list[dict]) -> str:
    lines = [
        "# Rewear — baseline vs agentic stylist (live Gemini)",
        "",
        "Baseline = single Gemini composition pass + deterministic validation.",
        "Agentic = ADK workflow: stylist → validation → multimodal critic → bounded refinement "
        f"(max_refinement_rounds={get_settings().max_refinement_rounds}).",
        "",
        "## Summary",
        "",
    ]
    lines += summarise(rows)
    lines += [
        "",
        "## Per case",
        "",
        "| Case | Engine | Objective checks | Looks | Latency | Rounds | Critic flags |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        failed = ", ".join(n for n, ok in r["checks"] if not ok) or "all pass"
        n_looks = len(r["gen"].looks) if r["gen"] else 0
        lines.append(
            f"| {r['case']['id']} | {r['engine']} ({r['actual_engine']}) | {failed} | {n_looks} "
            f"| {r['latency_ms']} ms | {r['rounds']} | {r['critic_flags']} |"
        )
    lines += [
        "",
        "## Side-by-side looks for human rating",
        "",
        "Rate each engine's output 1–5 for coherence, inspiration fidelity and styling usefulness.",
        "",
    ]
    for case_id in dict.fromkeys(r["case"]["id"] for r in rows):
        pair = [r for r in rows if r["case"]["id"] == case_id]
        lines += [f"### {case_id}", "", f"_{pair[0]['case']['description']}_", ""]
        for r in pair:
            g = r["gen"]
            lines.append(f"**{r['engine']}** — human rating: ___/5")
            if not g:
                lines.append("- (error)")
            elif not g.looks:
                lines.append(f"- No looks: {g.no_match_reason}")
            for lk in g.looks if g else []:
                lines += render_look(lk)
            if g and g.trace:
                lines.append("- Workflow: " + " → ".join(s.summary for s in g.trace.steps))
            lines.append("")
    return "\n".join(lines)


async def main(only: str | None, concurrency: int) -> int:
    if get_ai() is None:
        print("Live comparison needs Gemini (set GOOGLE_CLOUD_PROJECT and AI_BACKEND=vertex).", file=sys.stderr)
        return 2
    sem = asyncio.Semaphore(concurrency)
    cases = load_cases(only)
    rows = list(await asyncio.gather(*(run_one(c, e, sem) for c in cases for e in ENGINES)))
    out = HERE / "results" / "compare.md"
    out.parent.mkdir(exist_ok=True)
    out.write_text(report(rows))
    print("\n".join(summarise(rows)))
    print(f"\nreport: {out}")
    return 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--only", choices=["real", "sample"])
    p.add_argument("--concurrency", type=int, default=3)
    a = p.parse_args()
    sys.exit(asyncio.run(main(a.only, a.concurrency)))

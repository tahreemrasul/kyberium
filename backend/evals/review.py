"""Build a compact human-review sheet from evals/results/compare.json.

    uv run python -m evals.review            # default 7 representative scenarios
    uv run python -m evals.review --cases real-denim-skirt exact-camel-work

Writes evals/results/human_review.md. Three things are kept strictly apart:
  * what each engine recommended (garments, how to wear, gaps),
  * the Gemini critic's verdicts (model judgements — NOT human ratings, NOT quality scores),
  * blank human-rating fields for team reviewers.
"""

import argparse
import json

from evals.run_evals import HERE

DEFAULT_CASES = [
    "real-denim-skirt",
    "real-satin-material-challenge",
    "real-emerald-evening",
    "real-no-good-outfit",
    "missing-key-piece",
    "exact-camel-work",
    "formal-occasion-constraint",
]
LABEL = {"single_pass": "Baseline (single pass)", "agentic": "Agentic (stylist + critic)"}


def _look_lines(lk: dict) -> list[str]:
    pieces = " + ".join(i["garment"]["name"] for i in lk["items"])
    out = [f"**{lk['title']}** ({lk['strategy']}): {pieces}"]
    if lk.get("styling_instructions"):
        out.append("How to wear: " + " / ".join(lk["styling_instructions"]))
    essential = [g["description"] for g in lk["gaps"] if g["essential"]]
    if essential:
        out.append("Essential gap: " + "; ".join(essential))
    if lk.get("deviations"):
        out.append("Declared deviations: " + "; ".join(lk["deviations"][:2]))
    return out


def _critic(gen: dict) -> str:
    steps = (gen.get("trace") or {}).get("steps") or []
    if not steps:
        return "— (no critic in this engine)"
    lines = []
    for s in steps:
        if s["step"] == "critic":
            lines.append(f"pass {s['round']}: {s['summary']}")
            lines += [d for d in s["details"] if d.startswith(("✓", "✗"))][:3]
    return "<br>".join(lines) or "— (critic not reached)"


def build(rows: list[dict], cases: dict[str, dict], selected: list[str]) -> str:
    by = {(r["case"], r["variant"]): r for r in rows}
    out = [
        "# Rewear — human review: baseline vs agentic",
        "",
        "Each scenario shows what the two engines recommended. The **Gemini critic** column records model "
        "judgements for transparency — they are not ratings and not quality scores. **Human rating** fields "
        "are blank on purpose: fill them in independently, ideally before reading the critic column.",
        "",
        "Scales (1–5): **Coherence** (one intentional outfit?) · **Fidelity** (keeps what makes the inspiration "
        "work, or reinterprets it convincingly?) · **Usefulness** (would you wear it; do the instructions help?).",
        "",
    ]
    for case_id in selected:
        pair = [(v, by.get((case_id, v))) for v in ("single_pass", "agentic")]
        if not any(r for _, r in pair):
            continue
        out += [f"## {case_id}", "", f"_{cases.get(case_id, {}).get('description', '')}_", ""]
        out += ["| | Recommendation | Latency | Gemini critic (model judgement) | Human rating |", "|---|---|---|---|---|"]
        for v, r in pair:
            if r is None:
                continue
            gen = r["generation"] or {}
            looks = gen.get("looks") or []
            if looks:
                rec = "<br><br>".join("<br>".join(_look_lines(lk)) for lk in looks)
            else:
                reason = (gen.get("no_match_reason") or "no looks")[:300]
                rec = f"**No looks** — _{r['empty_reason'] or 'n/a'}_<br>{reason}"
            if gen.get("engine_note"):
                rec += f"<br>_note: {gen['engine_note']}_"
            out.append(
                f"| **{LABEL[v]}** | {rec} | {r['latency_ms'] / 1000:.0f} s | {_critic(gen)} "
                "| Coherence __ · Fidelity __ · Usefulness __ |"
            )
        out += ["", "Preferred: ☐ baseline ☐ agentic ☐ tie — Reviewer: ____ — Notes: ____", ""]
    out += [
        "## No-match classification (all runs)",
        "",
        "- **legitimate no-match** — the scenario expects an honest 'nothing convincing' answer;",
        "- **possible over-rejection** — the stylist proposed valid looks but the critic rejected them all;",
        "- **stylist declined** — no proposal was made; check whether a coherent outfit existed.",
        "",
        "| Case | Engine | Classification |",
        "|---|---|---|",
    ]
    out += [f"| {r['case']} | {r['variant']} | {r['empty_reason']} |" for r in rows if r["empty_reason"]]
    return "\n".join(out) + "\n"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--cases", nargs="*", default=DEFAULT_CASES)
    p.add_argument("--source", default="compare.json")
    a = p.parse_args()
    rows = json.loads((HERE / "results" / a.source).read_text())
    cases = {c["id"]: c for f in ("cases.json", "real_cases.json") for c in json.loads((HERE / f).read_text())}
    target = HERE / "results" / "human_review.md"
    target.write_text(build(rows, cases, a.cases))
    print(f"wrote {target}")


if __name__ == "__main__":
    main()

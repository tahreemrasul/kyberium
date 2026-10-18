# Agentic stylist: Outfit DNA, stylist, critic and refinement

This document describes the second-generation recommendation pipeline. The first version made a single Gemini pass that reasoned slot by slot. Version 2 composes **whole outfits**, has an **independent critic** review them, and **revises** before anything reaches the styling board.

## Why we changed the pipeline

In version 1, all substitution reasoning happened in one Gemini call (`app/pipeline/composer.py`). Its inputs were per-slot candidate lists and its output was per-garment explanations. Five problems followed:

1. The inspiration analysis described *garments*, not what makes the *outfit* work: waist definition, volume balance, contrast, texture, and which traits are essential.
2. Material wasn't visible to the composer. Neither inspiration pieces nor the composer payload carried `material_appearance`, so "denim skirt → satin skirt" looked like a clean midi-skirt match.
3. Candidates arrived as scores without *differences* (changes in drape, formality or contrast) or *compensations* ("half-tuck the sweater").
4. The output schema asked for per-item explanations, so the model rationalised each swap individually. There was no field for outfit coherence or how to wear the look.
5. Nothing judged the result. Plausible-sounding but incoherent combinations always shipped.

## Pipeline

```text
Inspiration photo ──► Gemini analyzer ──► OutfitDNA
                                           │  (pieces + essential/flexible traits, waist, volume,
                                           │   contrast, materials, styling details)
                 ┌─────────────────────────┴───────────────────────────┐
                 ▼                                                     ▼
   Wardrobe retrieval (deterministic)                Fashion knowledge retrieval (optional)
   ranked owned candidates + matching_attributes,     problem-driven query, e.g. "Preserve: defined
   differences, styling_considerations                 waist. Challenges: fluid satin instead of denim"
                 └─────────────────────────┬───────────────────────────┘
                                           ▼
             ┌──────────── Google ADK graph Workflow (app/stylist/workflow.py) ───────────┐
             │                                                                            │
             │  stylist (LlmAgent) ──► validate (deterministic) ──critique──► critic      │
             │     ▲                        │ done                     (LlmAgent, sees  │
             │     │ revise                 ▼                          garment images)  │
             │     └───────── decide (deterministic routing) ◄──────────────┘           │
             │                    │ done (approved looks only, ≤ max_refinement_rounds) │
             └────────────────────┴──────────────────────────────────────────────────────┘
                                           ▼
                Styling board: approved looks, How to wear it, critic badge, decision trace
```

| Component | Kind | Code |
|---|---|---|
| Outfit DNA analyzer | Gemini (structured output) | `app/pipeline/inspiration.py`, prompt `INSPIRATION_SYSTEM` |
| Candidate retrieval with differences | Deterministic | `app/pipeline/retrieval.py`, `app/pipeline/comparison.py` |
| Fashion knowledge | Pluggable tool (`none`/`local`/`vector`) | `app/knowledge/retriever.py` |
| Stylist | ADK `LlmAgent`, output schema `CompositionResult` | `app/stylist/workflow.py`, `prompts.py` |
| Validation | Deterministic (owned IDs, caps, occasion, keep/exclude) | `app/pipeline/validation.py` |
| Critic | ADK `LlmAgent`, output `CriticReport`, receives inspiration and garment images | `app/stylist/workflow.py` |
| Revision controller | Deterministic `decide` node, bounded | `StylingRun.on_decide` |

**Why the ADK graph `Workflow`.** We use ADK 2.12's graph workflow rather than a free-running multi-agent setup. It gives explicit state (`proposal`, `pending`, `accepted`, `critique`, `revision_brief`), explicit routes (`critique` / `revise` / `done`), per-node retries on 429s and transient errors, and a hard bound on the loop. Only the two genuinely creative and judgemental steps are LLM agents. Everything else is ordinary, testable Python.

## Role-level substitution

Slot-by-slot retrieval treated a belted shirt-dress as a poor "shirt" and a poor "skirt", and the
look schema could not express one garment filling two roles, so a dress covering top + skirt left
an "essential gap". Three generic changes fix this (no garment is special-cased):

- `app/pipeline/roles.py` scores one-piece garments against the inspiration's top + bottom
  **together** (waist definition, lower line, formality, palette, style) and passes them to the
  stylist as `multi_role_candidates` with differences and styling considerations.
- Items carry `covers_slot_ids`; validation and impact credit every role a garment fills (only
  one-piece garments may take on a bottom role).
- The stylist prompt asks it to think in roles, not categories (one piece → several roles,
  two pieces → one role).

Result on the reported case: the creative look is now the belted shirt-dress + sneakers
(critic-approved), alongside the closest sweater + wide-leg look.

## Decision rules (`on_decide`)

- **Approved:** verdict `approve` with no critical issue, or verdict `revise` with only minor issues. (This guards against inconsistent verdicts.)
- **What blocks a look:** only *actionable* issues. The critic marks each issue `fixable_with_wardrobe`. An unfixable fidelity gap ("no white shirt is owned") becomes a note on the look rather than triggering a pointless revision. Unfixable *critical* incoherence or occasion mismatches still block.
- **Revision:** looks that fail get revised once by default (`MAX_REFINEMENT_ROUNDS`, 0–2). The stylist receives the critic's specific issues and fixes, plus the already-approved looks so it doesn't duplicate them.
- **What the user sees:** only approved looks. If none survive, the board shows an honest explanation, including what didn't work. Rejected looks are never presented as matches.
- **Trace:** every pass is recorded in `Generation.trace` (summary, details, latency, tokens) and logged as JSON. The UI shows it under "How your stylist decided".

## Configuration

| Variable | Default | Effect |
|---|---|---|
| `STYLING_ENGINE` | `agentic` | `single_pass` runs the original composer (the baseline) |
| `CRITIC_ENABLED` | `true` | `false` turns the workflow into stylist → validate only |
| `MAX_REFINEMENT_ROUNDS` | `1` | Each round adds roughly one stylist call and one critic call (about 15–20 s) |
| `CRITIC_USES_IMAGES` | `true` | Sends the inspiration and garment thumbnails (384 px) to the critic |
| `AGENTIC_TIMEOUT_S` | `90` | On timeout or error, falls back to a labelled single pass, then to rules |
| `STYLIST_THINKING_BUDGET`, `CRITIC_THINKING_BUDGET` | `1024`, `512` | Gemini 2.5 thinking budgets |

If the workflow fails (model error or timeout), `/looks/generate` returns single-pass looks with a visible note that they were not critic-reviewed. The demo cannot hard-fail because of the agent layer.

## Evaluation

```bash
cd backend
uv run pytest -q tests/test_agentic.py          # graph runs offline with a scripted fake Gemini
uv run python -m evals.compare                  # live: single_pass vs agentic → evals/results/compare.md
uv run python -m evals.compare --only real      # the team's real wardrobe (photos stay local, out of git)
```

`evals/real_cases.json` reproduces the reported failure (white tucked shirt + denim midi skirt → a 7-piece real wardrobe) together with a material challenge, a cross-occasion case and a "no good outfit exists" case. `compare.md` reports objective checks, invalid-ID counts, latency and tokens, and lists both engines' looks side by side with blank **human rating** fields. The critic's verdicts are judgements, not quality scores.

## Latency and cost (live, Gemini 2.5 Flash, 16 cases)

Every generation records `timings` (per stage, both engines). Medians from `evals/results/compare.md`:

| Stage | Agentic | Baseline |
|---|---|---|
| Deterministic retrieval | 25 ms | 22 ms |
| Knowledge retrieval (local cards) | <1 ms | <1 ms |
| Stylist model time (all passes) | 19.4 s | — |
| Critic model time (all passes) | 12.6 s | — |
| Critic image prep / images / image tokens | 54 ms / 12 / ~3.1k | — |
| Revision passes (model time after pass 1) | 14.6 s | — |
| Composer (single pass) | — | 10.8 s |
| **Total** | **32 s** (max 105 s*) | **11 s** |

\* one run hit the 90 s budget during Vertex 429 bursts and fell back to a labelled single pass.

Ablation on the real-wardrobe cases (`agentic` vs `agentic_no_images` vs `agentic_no_revision`):
images add ~20 ms and ~1k tokens with no measurable latency cost; the stylist is ~60 % of model
time and the critic ~40 %; one revision round adds ~7 s median but roughly doubles the looks that
pass the critic. Default: one revision round, images on.

## Optional web search (not enabled)

ADK provides a built-in `google_search` tool (Gemini grounding). We have deliberately not wired it into the stylist yet:
- Built-in grounding tools can't be combined with structured `output_schema` in the same agent, so search would need its own sub-agent call. That adds latency and cost to every look.
- Our use cases are rare (unfamiliar aesthetics, product availability, verifying ethical claims).

The interface for adding it is the `FashionKnowledgeRetriever` seam: a search-backed retriever can return `FashionKnowledgeHit`s with `source_url` citations, with a per-request budget, without changing the stylist or the API.

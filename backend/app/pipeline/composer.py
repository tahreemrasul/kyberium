"""Step 4 — outfit composition.

``compose_with_gemini`` asks Gemini to reason over whole outfits using only the
shortlisted owned garments. ``compose_with_rules`` is the deterministic,
explicitly labelled fallback (demo mode / AI outage). Both return raw
``ComposedLook``s that must pass ``validation.build_looks``.
"""

import json

from app.ai.client import GeminiClient
from app.ai.prompts import COMPOSER_SYSTEM
from app.knowledge import FashionKnowledgeHit
from app.pipeline.attributes import color_family
from app.pipeline.retrieval import MIN_SCORE
from app.pipeline.validation import default_gap_reason, is_essential
from app.schemas import (
    CandidateMatch,
    ComposedGap,
    ComposedItem,
    ComposedLook,
    CompositionResult,
    Garment,
    InspirationAnalysis,
    InspirationPiece,
    StylePreferences,
)


def _garment_brief(g: Garment) -> dict:
    return {
        "id": g.id,
        "name": g.name,
        "category": g.category,
        "subcategory": g.subcategory,
        "colors": g.colors,
        "silhouette": g.silhouette,
        "pattern": g.pattern,
        "formality": g.formality,
        "layer": g.layer,
        "style_tags": g.style_tags,
    }


def build_composer_payload(
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
    candidates: dict[str, list[CandidateMatch]],
    wardrobe: dict[str, Garment],
    knowledge: list[FashionKnowledgeHit],
) -> dict:
    shortlisted = {c.garment_id for cs in candidates.values() for c in cs}
    others = [g for gid, g in wardrobe.items() if gid not in shortlisted][:60]
    return {
        "inspiration": analysis.model_dump(),
        "preferences": prefs.model_dump(),
        "candidates_per_slot": {
            slot: [
                {**_garment_brief(wardrobe[c.garment_id]), "rank_score": c.score, "match_notes": c.reasons}
                for c in cs
                if c.garment_id in wardrobe
            ]
            for slot, cs in candidates.items()
        },
        "other_owned_garments": [
            {"id": g.id, "name": g.name, "category": g.category, "colors": g.colors, "formality": g.formality}
            for g in others
        ],
        "owned_garment_ids": sorted(wardrobe),
        "styling_principles": [{"id": k.id, "text": k.text} for k in knowledge],
        "note": "rank_score is a heuristic ranking value, not a probability.",
    }


async def compose_with_gemini(
    ai: GeminiClient,
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
    candidates: dict[str, list[CandidateMatch]],
    wardrobe: dict[str, Garment],
    knowledge: list[FashionKnowledgeHit],
) -> CompositionResult:
    payload = build_composer_payload(analysis, prefs, candidates, wardrobe, knowledge)
    return await ai.generate_json(
        schema=CompositionResult,
        system=COMPOSER_SYSTEM,
        contents=["Compose looks for this request:\n" + json.dumps(payload)],
        model=ai.settings.composer_model,
        temperature=0.6,
        thinking_budget=1024,
        label="compose",
    )


# ---------------------------------------------------------------------------
# Deterministic fallback
# ---------------------------------------------------------------------------


def _explain(g: Garment, piece: InspirationPiece, reasons: list[str]) -> tuple[str, list[str], list[str]]:
    preserved = [r for r in reasons if " instead of " not in r and "standing in" not in r][:3]
    changed: list[str] = []
    if piece.colors and color_family(g.colors[0]) != color_family(piece.colors[0]):
        changed.append(f"{g.colors[0]} instead of {piece.colors[0]}")
    if g.category != piece.category:
        changed.append(f"a {g.subcategory or g.category} in place of the {piece.subcategory or piece.category}")
    detail = "; ".join(preserved[:2]) if preserved else "it fills the same role in the outfit"
    text = f"Your {g.name.lower()} can stand in for the {piece.description.rstrip('.').lower()} — {detail}."
    return text, preserved, changed


def _pick(
    piece: InspirationPiece,
    cands: list[CandidateMatch],
    wardrobe: dict[str, Garment],
    used: set[str],
    avoid: str | None = None,
    prefer_new_color: bool = False,
) -> CandidateMatch | None:
    pool = [c for c in cands if c.garment_id in wardrobe and c.garment_id not in used and c.garment_id != avoid]
    if prefer_new_color and piece.colors:
        base = color_family(piece.colors[0])
        varied = [c for c in pool if color_family(wardrobe[c.garment_id].colors[0]) != base]
        if varied and varied[0].score >= MIN_SCORE:
            return varied[0]
    return pool[0] if pool else None


_TITLES = {"closest": "Closest recreation", "creative": "Creative remix", "alternative": "Alternative interpretation"}


def _rule_look(
    strategy: str,
    analysis: InspirationAnalysis,
    candidates: dict[str, list[CandidateMatch]],
    wardrobe: dict[str, Garment],
    prefs: StylePreferences,
    baseline: dict[str, str] | None = None,
) -> tuple[ComposedLook, dict[str, str]]:
    used: set[str] = set()
    singles: set[str] = set()
    items: list[ComposedItem] = []
    gaps: list[ComposedGap] = []
    chosen: dict[str, str] = {}
    has_separates = bool({p.category for p in analysis.pieces} & {"top", "bottom"})
    # Fill defining pieces first so accessories never crowd them out.
    pieces = sorted(analysis.pieces, key=lambda p: (p.importance != "key", p.category == "dress"))

    def add(g: Garment, piece: InspirationPiece, reasons: list[str]) -> None:
        text, keep, change = _explain(g, piece, reasons)
        items.append(
            ComposedItem(
                garment_id=g.id, replaces_slot_id=piece.slot_id, explanation=text, preserved=keep, changed=change
            )
        )
        used.add(g.id)
        if g.category in ("bottom", "shoes", "dress"):
            singles.add(g.category)

    for piece in pieces:
        blocked = set(singles)
        if "dress" in singles:
            blocked.add("bottom")
        if "bottom" in singles:
            blocked.add("dress")
        cands = [
            c
            for c in candidates.get(piece.slot_id, [])
            if c.garment_id in wardrobe and wardrobe[c.garment_id].category not in blocked
        ]
        avoid = baseline.get(piece.slot_id) if baseline else None
        kept = [c for c in cands if c.garment_id in prefs.keep_garment_ids and c.garment_id not in used]
        pick = kept[0] if kept else None  # "keep this piece" is a hard constraint in every look
        pick = pick or _pick(piece, cands, wardrobe, used, avoid=avoid, prefer_new_color=strategy == "creative")
        if pick is None and avoid:
            pick = _pick(piece, cands, wardrobe, used)
        if pick is None:
            gaps.append(
                ComposedGap(slot_id=piece.slot_id, reason=default_gap_reason(piece), essential=is_essential(piece))
            )
            continue
        if piece.category == "dress":
            # Prefer an owned dress; otherwise a two-piece can replace it when the inspiration has no separates.
            order = [pick] + [c for c in cands if c is not pick and c.garment_id not in used]
            done = False
            for cand in order:
                g = wardrobe[cand.garment_id]
                if g.category == "dress" and cand.garment_id != avoid:
                    add(g, piece, cand.reasons)
                    done = True
                elif g.category in ("top", "bottom") and not has_separates:
                    other_cat = "bottom" if g.category == "top" else "top"
                    partner = next(
                        (c for c in cands if c.garment_id not in used and wardrobe[c.garment_id].category == other_cat),
                        None,
                    )
                    if partner:
                        add(g, piece, cand.reasons)
                        add(wardrobe[partner.garment_id], piece, partner.reasons)
                        done = True
                if done:
                    chosen[piece.slot_id] = g.id
                    break
            if not done:
                gaps.append(ComposedGap(slot_id=piece.slot_id, reason=default_gap_reason(piece), essential=True))
            continue
        g = wardrobe[pick.garment_id]
        add(g, piece, pick.reasons)
        chosen[piece.slot_id] = g.id

    why = []
    if analysis.proportions:
        why.append(f"Keeps the inspiration's proportions: {analysis.proportions.rstrip('.')}.")
    if strategy == "creative":
        why.append("Varies colours and pieces from your closet while keeping each garment's role.")
    else:
        why.append("Uses the owned pieces closest in type, cut and colour to each inspiration piece.")
    why.append(f"Chosen to suit a {prefs.occasion} setting.")
    return ComposedLook(strategy=strategy, title=_TITLES[strategy], items=items, gaps=gaps, why_it_works=why), chosen


def compose_with_rules(
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
    candidates: dict[str, list[CandidateMatch]],
    wardrobe: dict[str, Garment],
) -> CompositionResult:
    if not analysis.pieces or not any(candidates.values()):
        return CompositionResult(looks=[], no_match_reason="No owned garments are a reasonable match for this outfit.")
    first, chosen = _rule_look("closest", analysis, candidates, wardrobe, prefs)
    second, _ = _rule_look("creative", analysis, candidates, wardrobe, prefs, baseline=chosen)
    looks = [first]
    if {i.garment_id for i in second.items} != {i.garment_id for i in first.items}:
        looks.append(second)
    return CompositionResult(looks=[lk for lk in looks if lk.items])

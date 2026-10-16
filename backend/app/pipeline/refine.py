"""Step 6 — refinement: garment swaps and free-text requests.

Free text is translated into *structured* preference changes (Gemini, or a
small keyword parser in demo mode) and the same grounded pipeline is re-run, so
refinement can never introduce garments the user doesn't own.
"""

import json
import re

from app.ai.client import AIError, GeminiClient
from app.ai.prompts import REFINE_SYSTEM
from app.errors import ApiError
from app.pipeline.attributes import garment_subtype
from app.pipeline.retrieval import score_garment
from app.pipeline.validation import compute_impact
from app.schemas import Garment, Generation, Look, LookItem, RefinementPlan, StylePreferences


def swap_item(gen: Generation, look_id: str, old_id: str, new_garment: Garment) -> Look:
    look = next((lk for lk in gen.looks if lk.id == look_id), None)
    if look is None:
        raise ApiError(404, "not_found", "That look was not found.")
    idx = next((i for i, it in enumerate(look.items) if it.garment_id == old_id), None)
    if idx is None:
        raise ApiError(400, "invalid_swap", "That garment isn't part of this look.")
    if any(it.garment_id == new_garment.id for it in look.items):
        raise ApiError(400, "invalid_swap", "That garment is already in this look.")
    old = look.items[idx]
    pair = {new_garment.category, old.garment.category}
    top = new_garment if new_garment.category == "top" else old.garment
    layer_swap = pair == {"top", "outerwear"} and top.layer == "mid"  # an open knit can play an outer layer
    if new_garment.category != old.garment.category and not layer_swap:
        raise ApiError(400, "invalid_swap", f"Pick another {old.garment.category} to swap in.")

    piece = next((p for p in gen.analysis.pieces if p.slot_id == old.replaces_slot_id), None)
    preserved: list[str] = []
    changed: list[str] = []
    if piece is not None:
        scored = score_garment(piece, new_garment, gen.preferences.model_copy(update={"exclude_garment_ids": []}))
        reasons = scored.reasons if scored else []
        preserved = [r for r in reasons if " instead of " not in r][:3]
        changed = [r for r in reasons if " instead of " in r][:2]
        target = piece.description.rstrip(".").lower()
        detail = "; ".join(preserved[:2]) or "a different take on the same role"
        explanation = f"You swapped in your {new_garment.name.lower()} for the {target} — {detail}."
    else:
        explanation = f"You swapped in your {new_garment.name.lower()}."
    look.items[idx] = LookItem(
        garment_id=new_garment.id,
        garment=new_garment,
        replaces_slot_id=old.replaces_slot_id,
        replaces_description=old.replaces_description,
        explanation=explanation,
        preserved=preserved,
        changed=changed,
    )
    look.impact = compute_impact(look.items, look.gaps, gen.analysis)
    return look


# --- free-text refinement --------------------------------------------------------

_KEYWORDS: list[tuple[re.Pattern[str], dict]] = [
    (re.compile(r"\b(formal|dressy|polished|professional)\b"), {"occasion": "work", "note": "more polished"}),
    (re.compile(r"\b(evening|party|event|wedding)\b"), {"occasion": "event"}),
    (re.compile(r"\b(casual|relaxed|weekend)\b"), {"occasion": "everyday", "note": "more relaxed"}),
    (re.compile(r"\btravel"), {"occasion": "travel"}),
    (re.compile(r"\b(closer|exact|similar)\b"), {"fidelity": "close"}),
    (re.compile(r"\b(creative|colou?rful|bold)\b"), {"fidelity": "creative", "note": "more colourful"}),
    (re.compile(r"\b(i already own|i own|no shopping|don't buy|no new)\b"), {"shopping": "wardrobe_first"}),
    (re.compile(r"\b(second ?hand|rental|rent|pre-?loved)\b"), {"shopping": "secondhand_rental"}),
]
_CATEGORY_WORDS = {
    "outerwear": ("outerwear", "jacket", "coat", "layer"),
    "top": ("top",),
    "bottom": ("bottom", "bottoms"),
    "dress": ("dress",),
    "shoes": ("shoes", "shoe", "footwear"),
    "accessory": ("accessory", "bag"),
}
_CHANGE = re.compile(r"\b(change|swap|replace|without|instead of|different|no|not|drop|lose)\b")


def _mentioned(clause: str, g: Garment) -> bool:
    words = set(re.findall(r"[a-z]+", clause))
    words |= {w.rstrip("s") for w in words}
    names = {
        garment_subtype(g) or "",
        (g.subcategory or "").lower(),
        *g.name.lower().split(),
        *_CATEGORY_WORDS.get(g.category, ()),
    }
    names |= {n.rstrip("s") for n in names}
    names -= {"", "the", "and", "with"}
    return bool(words & names)


def keyword_plan(instruction: str, look: Look | None) -> RefinementPlan:
    text = instruction.lower()
    plan = RefinementPlan(summary="Updated your preferences and restyled the look.")
    notes: list[str] = []
    for pattern, change in _KEYWORDS:
        if pattern.search(text):
            for k in ("occasion", "fidelity", "shopping"):
                if k in change:
                    setattr(plan, k, change[k])
            if "note" in change:
                notes.append(change["note"])
    if look:
        # "Keep the blazer, but change the trousers" -> clause-level intent.
        for clause in re.split(r"\bbut\b|,|;|\band\b", text):
            keep = "keep" in clause
            drop = bool(_CHANGE.search(clause)) or "sneakers instead" in clause
            for it in look.items:
                if not _mentioned(clause, it.garment):
                    continue
                if keep and not drop:
                    plan.keep_garment_ids.append(it.garment_id)
                elif drop:
                    plan.exclude_garment_ids.append(it.garment_id)
    plan.notes = ", ".join(notes) or instruction
    return plan


async def plan_refinement(
    ai: GeminiClient | None, instruction: str, gen: Generation, look: Look | None, wardrobe: dict[str, Garment]
) -> RefinementPlan:
    if ai is None:
        return keyword_plan(instruction, look)
    payload = {
        "instruction": instruction,
        "current_preferences": gen.preferences.model_dump(),
        "current_look": [
            {"id": it.garment_id, "name": it.garment.name, "category": it.garment.category}
            for it in (look.items if look else [])
        ],
        "owned_garments": [{"id": g.id, "name": g.name, "category": g.category} for g in wardrobe.values()],
    }
    try:
        return await ai.generate_json(
            schema=RefinementPlan,
            system=REFINE_SYSTEM,
            contents=[json.dumps(payload)],
            temperature=0.1,
            thinking_budget=0,
            label="refine",
        )
    except AIError:
        return keyword_plan(instruction, look)


def apply_plan(prefs: StylePreferences, plan: RefinementPlan, wardrobe: dict[str, Garment]) -> StylePreferences:
    keep = [g for g in dict.fromkeys(prefs.keep_garment_ids + plan.keep_garment_ids) if g in wardrobe]
    exclude = [g for g in dict.fromkeys(prefs.exclude_garment_ids + plan.exclude_garment_ids) if g in wardrobe]
    exclude = [g for g in exclude if g not in plan.keep_garment_ids]
    keep = [g for g in keep if g not in plan.exclude_garment_ids]
    notes = (plan.notes or prefs.notes or "")[:300] or None
    return StylePreferences(
        occasion=plan.occasion or prefs.occasion,
        fidelity=plan.fidelity or prefs.fidelity,
        shopping=plan.shopping or prefs.shopping,
        keep_garment_ids=keep[:10],
        exclude_garment_ids=exclude[:40],
        notes=notes,
    )

"""Step 4b/5 — validate composed looks against the real wardrobe and compute
grounded impact numbers server-side (model-reported counts are never trusted).

Guarantees for every returned Look:
  * every item references a garment id owned by the current user;
  * no duplicate garments, at most one bottom / shoes / dress, no dress+bottom;
  * user exclusions honoured, clearly unsuitable occasion items removed;
  * every inspiration slot is either covered by an owned item or listed as a gap;
  * sourcing hints appear only when the shopping preference allows it.
"""

import uuid

from app.pipeline.attributes import occasion_fit
from app.schemas import (
    ComposedLook,
    Garment,
    ImpactSummary,
    InspirationAnalysis,
    InspirationPiece,
    Look,
    LookGap,
    LookItem,
    StylePreferences,
)

_SINGLE = {"bottom", "shoes", "dress"}
_STRATEGY_ORDER = {"closest": 0, "creative": 1, "alternative": 2}
_DISPLAY_ORDER = {"outerwear": 0, "top": 1, "dress": 2, "bottom": 3, "shoes": 4, "accessory": 5}


def sourcing_hint(piece: InspirationPiece, prefs: StylePreferences) -> str | None:
    desc = piece.description.rstrip(".")
    if prefs.shopping == "secondhand_rental":
        return f"If you'd like this piece, look for a pre-loved or rental {desc}."
    if prefs.shopping == "open_to_new":
        return f"If you decide to buy, choose a versatile {desc} you'll re-wear — checking secondhand first."
    return None


def default_gap_reason(piece: InspirationPiece) -> str:
    return f"Nothing in your closet fills the role of the {piece.description.rstrip('.')}."


def is_essential(piece: InspirationPiece) -> bool:
    return piece.importance == "key" and piece.category not in ("accessory",)


def covered_slots(items: list[LookItem]) -> set[str]:
    out: set[str] = set()
    for i in items:
        if i.replaces_slot_id:
            out.add(i.replaces_slot_id)
        out.update(i.covers_slot_ids)
    return out


def _may_cover(g: Garment, piece: InspirationPiece) -> bool:
    """Which extra roles a garment can plausibly take on besides its main one."""
    if g.category == piece.category:
        return True
    if g.category == "dress":
        return piece.category in ("top", "bottom")
    if g.category in ("top", "outerwear"):
        return piece.category in ("top", "outerwear")
    return False


def compute_impact(items: list[LookItem], gaps: list[LookGap], analysis: InspirationAnalysis) -> ImpactSummary:
    total = len(analysis.pieces)
    covered = len(covered_slots(items))
    essential = sum(1 for g in gaps if g.essential)
    owned = len(items)
    if not gaps:
        headline = f"{owned}/{owned} pieces already in your closet · No new purchase needed"
    elif essential == 0:
        headline = (
            f"{covered}/{total} inspiration pieces recreated from your closet · "
            "No purchase needed — the gaps are optional"
        )
    else:
        headline = f"{covered}/{total} inspiration pieces from your closet · {essential} wardrobe gap" + (
            "s" if essential > 1 else ""
        )
    return ImpactSummary(
        owned_count=owned,
        total_pieces=total,
        gap_count=len(gaps),
        essential_gap_count=essential,
        purchase_needed=essential > 0,
        potential_purchases_avoided=covered,
        headline=headline,
    )


def build_look(
    composed: ComposedLook,
    wardrobe: dict[str, Garment],
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
) -> Look | None:
    slots = {p.slot_id: p for p in analysis.pieces}
    warnings: list[str] = []
    items: list[LookItem] = []
    used: set[str] = set()
    single_used: set[str] = set()

    for ci in composed.items:
        g = wardrobe.get(ci.garment_id)
        if g is None:
            warnings.append("Removed a suggested piece that isn't in your closet.")
            continue
        if g.id in used:
            continue
        if g.id in prefs.exclude_garment_ids:
            warnings.append(f"Left out {g.name} as you asked.")
            continue
        if occasion_fit(g, prefs.occasion) == "poor":
            warnings.append(f"Left out {g.name}: it doesn't suit a {prefs.occasion} setting.")
            continue
        if g.category in _SINGLE:
            clash = g.category in single_used or (
                (g.category == "dress" and "bottom" in single_used)
                or (g.category == "bottom" and "dress" in single_used)
            )
            if clash:
                warnings.append(f"Left out {g.name}: the look already has a {g.category}.")
                continue
            single_used.add(g.category)
        slot = ci.replaces_slot_id if ci.replaces_slot_id in slots else None
        # One garment may fill several roles (a shirt-dress for top + skirt). Only one-piece garments
        # may also cover a bottom, so a top can never "cover" the trousers.
        extra = [
            s_id
            for s_id in dict.fromkeys(ci.covers_slot_ids)
            if s_id in slots and s_id != slot and _may_cover(g, slots[s_id])
        ]
        if slot is None and extra:
            slot, extra = extra[0], extra[1:]
        used.add(g.id)
        descs = [slots[x].description for x in ([slot] if slot else []) + extra]
        items.append(
            LookItem(
                garment_id=g.id,
                garment=g,
                replaces_slot_id=slot,
                covers_slot_ids=extra,
                replaces_description=" + ".join(descs) if descs else None,
                explanation=ci.explanation.strip() or f"{g.name} completes the look.",
                preserved=[s for s in ci.preserved if s.strip()][:5],
                changed=[s for s in ci.changed if s.strip()][:5],
                role=(ci.role or "").strip() or None,
            )
        )

    # "Keep this piece" is a hard user constraint: if the composer dropped a kept garment,
    # put it back in place of the item in the same category (or in a slot it fits).
    for gid in prefs.keep_garment_ids:
        g = wardrobe.get(gid)
        if g is None or gid in used:
            continue
        idx = next((i for i, it in enumerate(items) if it.garment.category == g.category), None)
        slot = (
            items[idx].replaces_slot_id
            if idx is not None
            else next((p.slot_id for p in analysis.pieces if p.category == g.category), None)
        )
        if idx is None and slot is None:
            continue
        kept = LookItem(
            garment_id=g.id,
            garment=g,
            replaces_slot_id=slot,
            replaces_description=slots[slot].description if slot else None,
            explanation=f"Your {g.name.lower()} stays in the look, as you asked.",
            preserved=[],
            changed=[],
        )
        if idx is None:
            items.append(kept)
        else:
            used.discard(items[idx].garment_id)
            items[idx] = kept
        used.add(g.id)

    if not items:
        return None
    items.sort(key=lambda it: _DISPLAY_ORDER.get(it.garment.category, 9))

    covered = covered_slots(items)
    gaps: list[LookGap] = []
    model_gaps = {cg.slot_id: cg for cg in composed.gaps if cg.slot_id in slots}
    for slot_id, piece in slots.items():
        if slot_id in covered:
            continue
        cg = model_gaps.get(slot_id)
        essential = cg.essential if cg else is_essential(piece)
        if piece.category == "accessory":
            essential = False
        gaps.append(
            LookGap(
                slot_id=slot_id,
                description=piece.description,
                category=piece.category,
                reason=(cg.reason.strip() if cg and cg.reason.strip() else default_gap_reason(piece)),
                essential=essential,
                sourcing_hint=sourcing_hint(piece, prefs),
            )
        )

    missing_keep = [gid for gid in prefs.keep_garment_ids if gid in wardrobe and gid not in used]
    if missing_keep:
        warnings.append("Couldn't fit every piece you asked to keep into this look.")

    return Look(
        id="lk_" + uuid.uuid4().hex[:12],
        strategy=composed.strategy,
        title=composed.title.strip()[:80] or "Your closet recreation",
        items=items,
        gaps=gaps,
        why_it_works=[w for w in composed.why_it_works if w.strip()][:4],
        styling_tip=composed.styling_tip,
        impact=compute_impact(items, gaps, analysis),
        warnings=list(dict.fromkeys(warnings)),
        coherence=(composed.coherence or "").strip() or None,
        styling_instructions=[x for x in composed.styling_instructions if x.strip()][:5],
        preserved_traits=[x for x in composed.preserved_traits if x.strip()][:6],
        deviations=[x for x in composed.deviations if x.strip()][:5],
    )


def build_looks(
    composed: list[ComposedLook],
    wardrobe: dict[str, Garment],
    analysis: InspirationAnalysis,
    prefs: StylePreferences,
    limit: int = 3,
) -> list[Look]:
    looks: list[Look] = []
    seen_sets: set[frozenset[str]] = set()
    seen_strategies: set[str] = set()
    for c in sorted(composed, key=lambda c: _STRATEGY_ORDER.get(c.strategy, 9)):
        look = build_look(c, wardrobe, analysis, prefs)
        if look is None:
            continue
        key = frozenset(i.garment_id for i in look.items)
        if key in seen_sets:
            continue
        if look.strategy in seen_strategies:
            look.strategy = "alternative" if "alternative" not in seen_strategies else look.strategy
        seen_sets.add(key)
        seen_strategies.add(look.strategy)
        looks.append(look)
        if len(looks) >= limit:
            break
    return looks

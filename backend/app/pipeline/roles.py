"""Role-level retrieval: one owned garment that fills SEVERAL inspiration roles at once.

Slot-by-slot retrieval scores a dress against "the shirt" and against "the skirt" separately,
so it looks like a poor match for both. But a one-piece garment can reproduce the *pair*:
a belted shirt-dress gives a shirt top, a defined waist and a skirt line. Here we score
one-piece garments (dresses, jumpsuits) against the inspiration's top + bottom together on
the qualities that make that pairing work — waist, lower-body line, formality, palette, style.

Deterministic and generic: no garment names are special-cased.
"""

import re

from app.pipeline.attributes import (
    color_similarity,
    formality_similarity,
    occasion_fit,
    silhouette_groups,
    style_similarity,
    subtype,
)
from app.pipeline.comparison import garment_material, material_of
from app.schemas import Garment, InspirationAnalysis, InspirationPiece, RoleCandidate, StylePreferences

ONE_PIECE = {"dress"}  # category; jumpsuits are tagged as dresses by the garment analyzer
_WAIST_WORDS = re.compile(r"belt|wrap|waist|fit-and-flare|fit and flare|cinched|tie|peplum")
_RANK = {"casual": 0, "smart_casual": 1, "formal": 2}
MIN_ROLE_SCORE = 0.5
WEIGHTS = {"waist": 0.25, "line": 0.25, "formality": 0.2, "style": 0.15, "color": 0.15}


def _waist_defined(text: str | None) -> bool:
    return bool(text) and "undefined" not in text.lower() and "no waist" not in text.lower()


def _garment_marks_waist(g: Garment) -> bool:
    text = " ".join(filter(None, [g.name, g.subcategory, g.silhouette, *g.style_tags]))
    return bool(_WAIST_WORDS.search(text.lower()))


def _text(p: InspirationPiece) -> str:
    return " ".join(filter(None, [p.silhouette, p.fit_volume, p.description]))


def score_role_garment(
    analysis: InspirationAnalysis, top: InspirationPiece, bottom: InspirationPiece, g: Garment, prefs: StylePreferences
) -> RoleCandidate | None:
    if g.category not in ONE_PIECE or g.id in prefs.exclude_garment_ids:
        return None
    if occasion_fit(g, prefs.occasion) == "poor":
        return None

    waist_needed = _waist_defined(analysis.waist_definition) or any("tuck" in d.lower() for d in top.styling_details)
    marks_waist = _garment_marks_waist(g)
    waist = 1.0 if (marks_waist or not waist_needed) else 0.3
    bottom_groups, g_groups = silhouette_groups(_text(bottom)), silhouette_groups(g.silhouette or g.name)
    shared_line = bottom_groups & g_groups
    line = 0.4 + 0.6 * len(shared_line) / max(1, len(bottom_groups)) if bottom_groups else 0.5
    formality = formality_similarity(g.formality, max(top.formality, bottom.formality, key=_RANK.get))
    color = 0.5 * color_similarity(top.colors, g.colors) + 0.5 * color_similarity(bottom.colors, g.colors)
    style = style_similarity(analysis.aesthetic + top.style_tags + bottom.style_tags, g.style_tags)
    score = (
        WEIGHTS["waist"] * waist
        + WEIGHTS["line"] * line
        + WEIGHTS["formality"] * formality
        + WEIGHTS["style"] * style
        + WEIGHTS["color"] * color
    )
    if g.id in prefs.keep_garment_ids:
        score = min(1.0, score + 0.25)

    matching = [f"one piece covering both the {top.description.lower()} and the {bottom.description.lower()}"]
    differences: list[str] = []
    tips: list[str] = []
    top_type = subtype(top.subcategory, top.description)
    if top_type and top_type == subtype(
        g.subcategory.replace("dress", "") if g.subcategory else None, g.name.replace("dress", "")
    ):
        matching.append(f"its {top_type} details echo the inspiration's {top_type}")
    if waist_needed and marks_waist:
        matching.append("marks the waist like the inspiration")
    elif waist_needed:
        differences.append("does not mark the waist on its own")
        tips.append("add a belt or tie to recreate the defined waist")
    if shared_line:
        matching.append("similar lower line: " + ", ".join(sorted(shared_line)))
    else:
        differences.append("different skirt shape or length from the inspiration's bottom")
    if formality >= 1.0:
        matching.append(f"matching formality ({g.formality.replace('_', ' ')})")
    if color < 0.6:
        top_c = top.colors[0] if top.colors else "top"
        bottom_c = bottom.colors[0] if bottom.colors else "bottom"
        differences.append(f"{g.colors[0]} replaces the inspiration's {top_c}/{bottom_c} two-tone contrast")
        tips.append("carry the inspiration's mood through shoes and accessories")
    bm, gm = material_of(bottom.material_appearance, bottom.description), garment_material(g)
    if bm and gm and bm != gm:
        differences.append(f"{gm} instead of {bm} in the lower half")
    differences.append("a single colour field instead of two separate pieces")
    return RoleCandidate(
        garment_id=g.id,
        covers_slot_ids=[top.slot_id, bottom.slot_id],
        score=round(min(score, 1.0), 3),
        matching_attributes=matching[:5],
        differences=differences[:4],
        styling_considerations=list(dict.fromkeys(tips))[:3],
    )


def rank_role_candidates(
    analysis: InspirationAnalysis, wardrobe: list[Garment], prefs: StylePreferences, top_k: int = 3
) -> list[RoleCandidate]:
    """One-piece garments that can stand in for the inspiration's top + bottom pair."""
    if any(p.category in ONE_PIECE for p in analysis.pieces):
        return []  # the inspiration already has a one-piece; slot retrieval handles dress <-> separates
    tops = [p for p in analysis.pieces if p.category == "top" and p.layer in ("base", "mid", "none")]
    bottoms = [p for p in analysis.pieces if p.category == "bottom"]
    if not tops or not bottoms:
        return []
    top, bottom = tops[0], bottoms[0]
    out = [c for g in wardrobe if (c := score_role_garment(analysis, top, bottom, g, prefs))]
    out = [c for c in out if c.score >= MIN_ROLE_SCORE or c.garment_id in prefs.keep_garment_ids]
    out.sort(key=lambda c: (-c.score, c.garment_id))
    return out[:top_k]

"""Step 3 — deterministic wardrobe retrieval.

For each inspiration slot, rank owned garments with hard filters (category
compatibility, occasion suitability, user exclusions) and weighted soft
signals modulated by the fidelity preference. Output feeds the composer.
"""

from dataclasses import dataclass

from app.pipeline.attributes import (
    color_family,
    color_similarity,
    formality_similarity,
    garment_subtype,
    occasion_fit,
    piece_subtype,
    silhouette_similarity,
    style_similarity,
    subtype_similarity,
)
from app.schemas import CandidateMatch, Garment, InspirationAnalysis, InspirationPiece, StylePreferences

WEIGHTS: dict[str, dict[str, float]] = {
    "close": {"color": 0.35, "silhouette": 0.22, "subtype": 0.20, "formality": 0.10, "style": 0.13},
    "aesthetic": {"color": 0.15, "silhouette": 0.27, "subtype": 0.15, "formality": 0.18, "style": 0.25},
    "creative": {"color": 0.05, "silhouette": 0.27, "subtype": 0.08, "formality": 0.25, "style": 0.35},
}
MIN_SCORE = 0.35
TOP_K = 5


def category_factor(piece: InspirationPiece, g: Garment) -> float:
    """0 = incompatible role. Substitutes are allowed with a penalty."""
    if g.category == piece.category:
        if piece.category == "accessory":
            ps, gs = piece_subtype(piece), garment_subtype(g)
            if ps and gs and ps != gs:
                return 0.0  # a tote can't stand in for earrings
        return 1.0
    if piece.category == "outerwear" and g.category == "top" and g.layer == "mid":
        return 0.75  # open cardigan/knit as a light outer layer
    if piece.category == "dress" and g.category in ("top", "bottom"):
        return 0.7  # two-piece standing in for a dress
    if piece.category in ("top", "bottom") and g.category == "dress":
        return 0.55
    return 0.0


@dataclass
class Scored:
    garment: Garment
    score: float
    reasons: list[str]


def score_garment(piece: InspirationPiece, g: Garment, prefs: StylePreferences) -> Scored | None:
    factor = category_factor(piece, g)
    if factor == 0.0 or g.id in prefs.exclude_garment_ids:
        return None
    fit = occasion_fit(g, prefs.occasion)
    if fit == "poor":
        return None
    w = WEIGHTS[prefs.fidelity]
    ps, gs = piece_subtype(piece), garment_subtype(g)
    sims = {
        "color": color_similarity(piece.colors, g.colors),
        "silhouette": silhouette_similarity(piece.silhouette or piece.description, g.silhouette or g.name),
        "subtype": subtype_similarity(ps, gs),
        "formality": formality_similarity(piece.formality, g.formality),
        "style": style_similarity(piece.style_tags, g.style_tags),
    }
    score = sum(w[k] * v for k, v in sims.items()) * factor * (1.0 if fit == "good" else 0.88)
    if g.id in prefs.keep_garment_ids:
        score = min(1.0, score + 0.25)

    reasons: list[str] = []
    if factor < 1.0:
        reasons.append(f"{g.category} standing in for the {piece.category}")
    elif ps and gs and ps == gs:
        reasons.append(f"same garment type ({gs})")
    if sims["silhouette"] >= 0.7:
        reasons.append(f"similar silhouette ({g.silhouette or 'cut'})")
    pf, gf = (color_family(piece.colors[0]) if piece.colors else None), color_family(g.colors[0])
    if sims["color"] >= 1.0:
        reasons.append(f"same colour family ({gf})")
    elif pf and gf:
        reasons.append(f"{g.colors[0]} instead of {piece.colors[0]}")
    if sims["formality"] >= 1.0:
        reasons.append(f"matching formality ({g.formality.replace('_', ' ')})")
    shared = sorted(set(piece.style_tags) & set(g.style_tags))
    if shared:
        reasons.append("shared style: " + ", ".join(shared[:3]))
    if fit == "good":
        reasons.append(f"suits {prefs.occasion}")
    return Scored(g, round(min(score, 1.0), 3), reasons)


def rank_candidates(
    analysis: InspirationAnalysis, wardrobe: list[Garment], prefs: StylePreferences, top_k: int = TOP_K
) -> dict[str, list[CandidateMatch]]:
    out: dict[str, list[CandidateMatch]] = {}
    for piece in analysis.pieces:
        scored = [s for g in wardrobe if (s := score_garment(piece, g, prefs))]
        # Garments the user asked to keep stay shortlisted whenever their role fits, regardless of score.
        kept = [s for s in scored if s.garment.id in prefs.keep_garment_ids]
        rest = [s for s in scored if s.score >= MIN_SCORE and s.garment.id not in prefs.keep_garment_ids]
        rest.sort(key=lambda s: (-s.score, s.garment.id))
        kept.sort(key=lambda s: (-s.score, s.garment.id))
        out[piece.slot_id] = [
            CandidateMatch(garment_id=s.garment.id, slot_id=piece.slot_id, score=s.score, reasons=s.reasons)
            for s in (kept + rest)[: max(top_k, len(kept))]
        ]
    return out

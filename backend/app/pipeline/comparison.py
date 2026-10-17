"""Deterministic piece-vs-garment comparison for the stylist.

For each wardrobe candidate we describe *what is kept*, *what changes* and *what
styling would compensate* — so the stylist reasons about trade-offs instead of a
bare similarity score. Heuristic, transparent, and testable.
"""

import re
from dataclasses import dataclass

from app.pipeline.attributes import NEUTRALS, color_family, silhouette_groups
from app.schemas import Garment, InspirationPiece

# material family -> (keywords, drape, finish, formality 0-2)
MATERIALS: dict[str, tuple[list[str], str, str, float]] = {
    "denim": (["denim", "jean", "chambray"], "structured", "matte", 0.0),
    "satin": (["satin", "silk", "slip", "charmeuse", "silky", "sheen"], "fluid", "lustrous", 1.8),
    "leather": (["leather", "patent", "faux leather"], "structured", "smooth", 1.2),
    "suede": (["suede", "nubuck"], "soft-structured", "napped", 1.0),
    "tweed": (["tweed", "boucle", "bouclé"], "textured", "textured", 1.6),
    "knit": (["knit", "sweater", "jumper", "cardigan", "cashmere", "ribbed", "cable"], "soft", "matte", 0.6),
    "suiting": (["suiting", "tailored", "wool", "crepe", "gabardine"], "structured", "matte", 1.5),
    "jersey": (["jersey", "t-shirt", "tee", "sweatshirt", "fleece"], "soft", "matte", 0.2),
    "cotton": (["cotton", "poplin", "oxford", "twill", "canvas", "linen", "chino"], "crisp", "matte", 0.9),
}
_LIGHT = {"white", "cream", "beige", "yellow"}
_DARK = {"black", "navy", "brown"}


def material_of(*texts: str | None) -> str | None:
    """Material family named earliest in the given texts (material field first)."""
    for text in texts:
        if not text:
            continue
        t = text.lower()
        best: tuple[int, str] | None = None
        for fam, (kws, *_rest) in MATERIALS.items():
            for kw in kws:
                m = re.search(rf"(?<![a-z]){re.escape(kw)}", t)
                if m and (best is None or m.start() < best[0]):
                    best = (m.start(), fam)
        if best:
            return best[1]
    return None


def piece_material(p: InspirationPiece) -> str | None:
    return material_of(p.material_appearance, p.description, p.subcategory)


def garment_material(g: Garment) -> str | None:
    return material_of(g.material_appearance, g.name, g.subcategory)


def _value(colors: list[str]) -> str | None:
    fam = color_family(colors[0]) if colors else None
    if fam is None:
        return None
    return "light" if fam in _LIGHT else "dark" if fam in _DARK else "mid"


def _volume(text: str | None) -> int:
    groups = silhouette_groups(text)
    return 1 if groups & {"relaxed", "wide"} else -1 if "fitted" in groups else 0


@dataclass
class Comparison:
    matching: list[str]
    differences: list[str]
    considerations: list[str]
    material_similarity: float


def compare(piece: InspirationPiece, g: Garment) -> Comparison:
    matching: list[str] = []
    diffs: list[str] = []
    tips: list[str] = []

    if g.category == piece.category:
        matching.append(f"same role ({piece.category})")
    else:
        diffs.append(f"a {g.subcategory or g.category} in place of the {piece.subcategory or piece.category}")

    # Colour and contrast
    pf = color_family(piece.colors[0]) if piece.colors else None
    gf = color_family(g.colors[0]) if g.colors else None
    if pf and gf and pf == gf:
        matching.append(f"same colour family ({gf})")
    elif pf and gf:
        diffs.append(f"{g.colors[0]} instead of {piece.colors[0]}")
        pv, gv = _value(piece.colors), _value(g.colors)
        if pv and gv and pv != gv and "mid" not in (pv, gv):
            diffs.append(f"flips the light/dark value ({pv} → {gv}), changing the outfit's contrast")
            tips.append("rebalance contrast elsewhere so the look doesn't turn flat or heavy")
        elif pf in NEUTRALS and gf not in NEUTRALS:
            diffs.append("introduces a colour accent where the inspiration was neutral")

    # Material, drape and formality of the fabric
    pm, gm = piece_material(piece), garment_material(g)
    mat_sim = 0.5
    if pm and gm:
        if pm == gm:
            matching.append(f"same material feel ({gm})")
            mat_sim = 1.0
        else:
            _, pdrape, pfinish, pform = MATERIALS[pm]
            _, gdrape, gfinish, gform = MATERIALS[gm]
            mat_sim = 0.6 if pdrape == gdrape else 0.25
            diff = f"{gdrape} {gm} instead of {pdrape} {pm}"
            if gfinish != pfinish:
                diff += f" ({gfinish} vs {pfinish} finish)"
            diffs.append(diff)
            if gform - pform >= 0.8:
                diffs.append("reads dressier than the original piece")
                tips.append("balance its polish with relaxed, casual partners to keep the original ease")
            elif pform - gform >= 0.8:
                diffs.append("reads more casual than the original piece")
                tips.append("pair with polished pieces so the look stays put-together")

    # Silhouette, length and volume
    pg = silhouette_groups(" ".join(filter(None, [piece.silhouette, piece.fit_volume, piece.description])))
    gg = silhouette_groups(" ".join(filter(None, [g.silhouette, g.name])))
    shared = pg & gg
    if shared:
        matching.append("similar cut: " + ", ".join(sorted(shared)))
    pvol = _volume(" ".join(filter(None, [piece.fit_volume, piece.silhouette])))
    gvol = _volume(g.silhouette)
    if gvol > pvol:
        diffs.append("more volume than the original")
        tips.append("counterbalance the extra volume with a slimmer partner or define the waist")
    elif gvol < pvol:
        diffs.append("slimmer than the original")
    if pg and gg and ("long" in pg) != ("long" in gg):
        diffs.append("different length, which shifts the outfit's proportions")
    if "cropped" in gg and g.category == "outerwear" and "cropped" not in pg:
        tips.append("a cropped layer moves the eye to the waist — keep the waistline visible")

    if g.formality == piece.formality:
        matching.append(f"matching formality ({g.formality.replace('_', ' ')})")

    # How the inspiration wears the piece
    details = " ".join(piece.styling_details).lower()
    if "tuck" in details and g.category in ("top", "dress"):
        if gm in ("knit", "jersey") or gvol > 0:
            tips.append("front-tuck or half-tuck it to keep the waist definition the inspiration relies on")
        else:
            tips.append("tuck it in, as in the inspiration")
    if ("open" in details or "unbuttoned" in details) and g.category in ("outerwear", "top") and g.layer != "base":
        tips.append("wear it open to keep the layered line")
    if "belt" in details:
        tips.append("add a belt if the piece doesn't mark the waist on its own")

    return Comparison(matching[:5], diffs[:5], list(dict.fromkeys(tips))[:4], mat_sim)

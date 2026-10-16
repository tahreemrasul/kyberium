"""Deterministic attribute normalisation and similarity for wardrobe matching.

All similarity values are heuristic ranking signals in [0, 1], not
calibrated probabilities.
"""

import re
from typing import Literal

from app.schemas import Garment, InspirationPiece, Occasion

# --- colour -------------------------------------------------------------------

COLOR_FAMILIES: dict[str, list[str]] = {
    "white": ["white", "ivory", "off-white", "off white", "snow", "optic white"],
    "cream": ["cream", "ecru", "oat", "oatmeal", "bone", "vanilla", "champagne", "buttercream"],
    "beige": ["beige", "camel", "tan", "sand", "khaki", "taupe", "stone", "nude", "biscuit", "fawn"],
    "brown": ["brown", "chocolate", "cognac", "mocha", "coffee", "chestnut", "espresso", "caramel"],
    "black": ["black", "jet", "onyx"],
    "grey": ["grey", "gray", "charcoal", "slate", "heather"],
    "navy": ["navy", "midnight", "indigo", "dark blue"],
    "blue": [
        "blue",
        "denim",
        "light wash",
        "light-wash",
        "mid wash",
        "mid-wash",
        "sky",
        "cobalt",
        "powder",
        "chambray",
        "cornflower",
    ],
    "green": ["green", "sage", "olive", "forest", "emerald", "mint", "moss", "bottle", "pistachio"],
    "red": ["red", "burgundy", "wine", "maroon", "cherry", "crimson", "oxblood"],
    "pink": ["pink", "blush", "rose", "fuchsia", "magenta", "dusty rose"],
    "orange": ["orange", "rust", "terracotta", "coral", "burnt", "copper", "apricot", "tangerine"],
    "yellow": ["yellow", "mustard", "butter", "lemon", "ochre"],
    "purple": ["purple", "lilac", "lavender", "plum", "violet", "mauve"],
    "metallic": ["gold", "silver", "metallic", "bronze"],
}
NEUTRALS = {"white", "cream", "beige", "brown", "black", "grey", "navy"}
_COLOR_KEYS = sorted(((kw, fam) for fam, kws in COLOR_FAMILIES.items() for kw in kws), key=lambda x: -len(x[0]))


def color_family(name: str) -> str | None:
    n = name.lower()
    for kw, fam in _COLOR_KEYS:
        if re.search(rf"(?<![a-z]){re.escape(kw)}(?![a-z])", n):
            return fam
    return None


def color_similarity(a: list[str], b: list[str]) -> float:
    fa = [f for f in (color_family(c) for c in a) if f]
    fb = [f for f in (color_family(c) for c in b) if f]
    if not fa or not fb:
        return 0.5
    if fa[0] == fb[0]:
        base = 1.0
    elif fa[0] in NEUTRALS and fb[0] in NEUTRALS:
        base = 0.6
    elif fa[0] in NEUTRALS or fb[0] in NEUTRALS:
        base = 0.3
    else:
        base = 0.15
    secondary = (
        len(set(fa[1:]) & set(fb[1:])) > 0 or (len(fa) > 1 and fa[1] == fb[0]) or (len(fb) > 1 and fb[1] == fa[0])
    )
    return min(1.0, base + (0.1 if secondary and base < 1 else 0))


# --- silhouette -----------------------------------------------------------------

SILHOUETTE_GROUPS: dict[str, list[str]] = {
    "relaxed": ["oversized", "relaxed", "loose", "boxy", "slouchy", "roomy", "dropped", "drop-shoulder"],
    "fitted": ["slim", "fitted", "skinny", "bodycon", "tight", "body-skimming", "sculpted"],
    "structured": ["structured", "tailored", "sharp", "crisp", "single-breasted", "double-breasted"],
    "wide": ["wide", "wide-leg", "flare", "flared", "palazzo", "a-line", "full", "bootcut", "barrel"],
    "straight": ["straight", "straight-leg", "column", "regular", "classic", "shift"],
    "cropped": ["cropped", "crop", "short"],
    "long": ["longline", "long", "maxi", "midi", "ankle", "full-length", "knee-length"],
    "fluid": ["bias", "bias-cut", "slip", "fluid", "draped", "wrap", "flowy", "satin"],
    "high_rise": ["high-rise", "high rise", "high-waisted", "high waisted"],
}
_SIL_KEYS = sorted(((kw, g) for g, kws in SILHOUETTE_GROUPS.items() for kw in kws), key=lambda x: -len(x[0]))


def silhouette_groups(text: str | None) -> set[str]:
    if not text:
        return set()
    t = text.lower()
    found: set[str] = set()
    for kw, g in _SIL_KEYS:
        if re.search(rf"(?<![a-z]){re.escape(kw)}(?![a-z])", t):
            found.add(g)
    return found


def silhouette_similarity(a: str | None, b: str | None) -> float:
    ga, gb = silhouette_groups(a), silhouette_groups(b)
    if not ga or not gb:
        return 0.5
    inter = len(ga & gb)
    if inter == 0:
        conflicting = ({"relaxed", "fitted"} <= (ga | gb)) or ({"wide", "fitted"} <= (ga | gb))
        return 0.1 if conflicting else 0.3
    return 0.4 + 0.6 * inter / len(ga | gb)


# --- garment type -------------------------------------------------------------

SUBTYPES: dict[str, list[str]] = {
    "blazer": ["blazer", "suit jacket", "sport coat", "tuxedo jacket"],
    "jacket": ["jacket", "bomber", "trucker", "denim jacket", "leather jacket", "shacket", "overshirt", "biker"],
    "coat": ["coat", "trench", "overcoat", "mac", "parka", "peacoat", "duster"],
    "tee": ["t-shirt", "tee", "tshirt"],
    "shirt": ["shirt", "blouse", "button-down", "button-up", "poplin"],
    "knit": ["sweater", "jumper", "cardigan", "knit", "pullover", "turtleneck"],
    "cami": ["cami", "camisole", "tank", "slip top", "vest top", "bodysuit"],
    "trousers": ["trousers", "pants", "slacks", "chinos", "culottes"],
    "jeans": ["jeans", "denim"],
    "skirt": ["skirt"],
    "shorts": ["shorts"],
    "dress": ["dress", "gown", "jumpsuit"],
    "sneakers": ["sneakers", "trainers", "sneaker"],
    "flats": ["loafers", "loafer", "flats", "ballet", "mules", "mary jane", "brogues", "oxfords"],
    "boots": ["boots", "booties", "ankle boots", "boot"],
    "heels": ["heels", "pumps", "heeled", "stilettos", "sandals", "slingbacks"],
    "bag": ["bag", "tote", "clutch", "handbag", "crossbody", "purse"],
    "jewellery": ["earrings", "necklace", "bracelet", "ring", "hoops", "jewelry", "jewellery"],
    "scarf": ["scarf", "bandana"],
    "belt": ["belt"],
    "hat": ["hat", "cap", "beanie"],
}
_RELATED = [
    {"blazer", "jacket", "coat"},
    {"tee", "shirt", "knit", "cami"},
    {"trousers", "jeans"},
    {"sneakers", "flats", "boots", "heels"},
    {"skirt", "trousers"},
]
_SUB_KEYS = sorted(((kw, s) for s, kws in SUBTYPES.items() for kw in kws), key=lambda x: -len(x[0]))


def subtype(*texts: str | None) -> str | None:
    for text in texts:
        if not text:
            continue
        t = text.lower()
        for kw, s in _SUB_KEYS:
            if re.search(rf"(?<![a-z]){re.escape(kw)}(?![a-z])", t):
                return s
    return None


def subtype_similarity(a: str | None, b: str | None) -> float:
    if not a or not b:
        return 0.5
    if a == b:
        return 1.0
    if any(a in grp and b in grp for grp in _RELATED):
        return 0.55
    return 0.2


# --- formality & occasion -------------------------------------------------------

_FORMALITY_RANK = {"casual": 0, "smart_casual": 1, "formal": 2}


def formality_similarity(a: str, b: str) -> float:
    return max(0.0, 1.0 - 0.45 * abs(_FORMALITY_RANK[a] - _FORMALITY_RANK[b]))


_UNSUITABLE_TAGS = {"athletic", "sporty", "gym", "activewear", "athleisure", "loungewear", "beach", "swim"}

OccasionFit = Literal["good", "ok", "poor"]


def occasion_fit(g: Garment, occasion: Occasion) -> OccasionFit:
    if occasion in g.occasions:
        return "good"
    tags = set(g.style_tags)
    if occasion == "work":
        if g.formality in ("smart_casual", "formal"):
            return "good"
        return "poor" if tags & _UNSUITABLE_TAGS else "ok"
    if occasion == "event":
        if g.formality == "formal":
            return "good"
        if g.formality == "smart_casual":
            return "ok"
        return "poor" if g.category != "accessory" else "ok"
    if occasion in ("everyday", "travel"):
        return "ok" if g.formality == "formal" else "good"
    return "ok"


def style_similarity(a: list[str], b: list[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa or not sb:
        return 0.4
    return min(1.0, 0.25 + len(sa & sb) / max(1, min(len(sa), len(sb))))


def piece_subtype(p: InspirationPiece) -> str | None:
    return subtype(p.subcategory, p.description)


def garment_subtype(g: Garment) -> str | None:
    return subtype(g.subcategory, g.name)

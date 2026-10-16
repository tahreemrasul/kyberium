"""Original flat-lay garment illustrations (SVG), authored for Rewear's sample
wardrobe so the demo needs no third-party photos. Shown in the UI with an
"illustration" label so they are never mistaken for real photos.
"""

import re
from html import escape

W, H = 400, 500


def _hex(c: str) -> tuple[int, int, int]:
    c = c.lstrip("#")
    return int(c[0:2], 16), int(c[2:4], 16), int(c[4:6], 16)


def shade(c: str, f: float) -> str:
    """f<0 darkens, f>0 lightens."""
    r, g, b = _hex(c)
    if f < 0:
        r, g, b = (int(v * (1 + f)) for v in (r, g, b))
    else:
        r, g, b = (int(v + (255 - v) * f) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def _mirror(path: str) -> str:
    """Mirror an absolute M/L/Q/Z path around x=200."""
    out, tokens = [], re.findall(r"[MLQZ]|-?\d+(?:\.\d+)?", path)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t in ("M", "L", "Q", "Z"):
            out.append(t)
            i += 1
            continue
        x, y = float(t), float(tokens[i + 1])
        out.append(f"{400 - x:g},{y:g}")
        i += 2
    return " ".join(out)


def _sym(path: str) -> list[str]:
    return [path, _mirror(path)]


# Each shape returns SVG markup given fill F (main), D (dark stroke), L (light accent), A (secondary).
def _blazer(F, D, L, A, long=False):
    hem = 470 if long else 430
    sl = "M138,88 L96,112 Q80,240 72,388 L108,394 Q118,260 134,190 Z"
    body = f"M138,88 L200,112 L262,88 L280,190 L292,{hem} L108,{hem} L120,190 Z"
    lapel = "M200,114 L160,94 L148,142 L172,152 L200,262 Z"
    parts = [f'<path d="{p}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>' for p in _sym(sl)]
    parts.append(f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>')
    parts.append(f'<path d="M160,94 L200,84 L240,94 L200,114 Z" fill="{shade(F, -0.25) if F.startswith("#") else D}"/>')
    parts += [
        f'<path d="{p}" fill="{L}" stroke="{D}" stroke-width="2.5" stroke-linejoin="round"/>' for p in _sym(lapel)
    ]
    parts.append(f'<line x1="200" y1="262" x2="200" y2="{hem}" stroke="{D}" stroke-width="2"/>')
    for y in (300, 340):
        parts.append(f'<circle cx="212" cy="{y}" r="5.5" fill="{D}"/>')
    if long:
        parts.append(f'<rect x="114" y="250" width="172" height="18" fill="{A}" stroke="{D}" stroke-width="2"/>')
        parts.append(f'<rect x="190" y="246" width="20" height="26" fill="none" stroke="{D}" stroke-width="3"/>')
        parts.append(f'<circle cx="188" cy="300" r="5.5" fill="{D}"/><circle cx="188" cy="340" r="5.5" fill="{D}"/>')
    parts.append(f'<path d="M128,360 L178,360 M222,360 L272,360" stroke="{D}" stroke-width="3"/>')
    return "".join(parts)


def _jacket(F, D, L, A, leather=False):
    sl = "M135,90 L92,115 Q80,220 76,330 L110,334 Q118,240 132,180 Z"
    body = "M135,90 L200,104 L265,90 L278,180 L284,345 L116,345 L122,180 Z"
    parts = [f'<path d="{p}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>' for p in _sym(sl)]
    parts.append(f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>')
    parts.append(
        f'<path d="M150,90 L200,110 L250,90 L244,70 L200,90 L156,70 Z" fill="{A}" stroke="{D}" stroke-width="2.5"/>'
    )
    parts.append(f'<rect x="116" y="318" width="168" height="27" fill="{A}" stroke="{D}" stroke-width="2.5"/>')
    if leather:
        parts.append(f'<path d="M226,104 L188,345" stroke="{L}" stroke-width="4"/>')
        parts.append(
            f'<path d="M150,92 L190,150 L170,175 M250,92 L226,104" fill="none" stroke="{L}" stroke-width="3"/>'
        )
    else:
        parts.append(f'<line x1="200" y1="110" x2="200" y2="345" stroke="{D}" stroke-width="2.5"/>')
        for x in (140, 216):
            parts.append(
                f'<rect x="{x}" y="150" width="44" height="36" rx="3" fill="none" stroke="{L}" stroke-width="2.5" stroke-dasharray="5 4"/>'
            )
        for y in (150, 200, 250, 300):
            parts.append(f'<circle cx="208" cy="{y}" r="4.5" fill="{L}"/>')
    return "".join(parts)


def _cardigan(F, D, L, A):
    sl = "M140,90 L98,114 Q82,250 78,384 L114,388 Q122,262 134,192 Z"
    body = "M140,88 L176,92 L200,250 L224,92 L260,88 L278,190 L286,420 L114,420 L122,190 Z"
    parts = [f'<path d="{p}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>' for p in _sym(sl)]
    parts.append(f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>')
    parts.append(f'<path d="M176,92 L200,250 L224,92 Q200,104 176,92 Z" fill="{A}"/>')
    parts.append(f'<line x1="200" y1="250" x2="200" y2="420" stroke="{D}" stroke-width="2"/>')
    for y in (280, 320, 360, 400):
        parts.append(f'<circle cx="206" cy="{y}" r="4.5" fill="{D}"/>')
    parts.append(f'<rect x="114" y="398" width="172" height="22" fill="{A}" stroke="{D}" stroke-width="2"/>')
    for x in range(140, 262, 24):  # cable texture
        parts.append(
            f'<path d="M{x},270 q8,12 0,24 q-8,12 0,24 q8,12 0,24 q-8,12 0,24" fill="none" stroke="{A}" stroke-width="3"/>'
        )
    return "".join(parts)


def _shirt(F, D, L, A, boxy=False):
    sl = "M140,92 L100,112 Q86,240 80,380 L112,386 Q122,260 136,190 Z"
    body = "M140,92 L180,82 L200,96 L220,82 L260,92 L276,190 L282,410 Q200,430 118,410 L124,190 Z"
    parts = [f'<path d="{p}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>' for p in _sym(sl)]
    parts.append(f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>')
    parts += [
        f'<path d="{p}" fill="{L}" stroke="{D}" stroke-width="2.5" stroke-linejoin="round"/>'
        for p in _sym("M180,82 L200,96 L186,124 L164,98 Z")
    ]
    parts.append(f'<line x1="200" y1="96" x2="200" y2="424" stroke="{D}" stroke-width="2"/>')
    for y in range(140, 420, 50):
        parts.append(f'<circle cx="206" cy="{y}" r="3.5" fill="{D}"/>')
    if boxy:
        for x in (142, 220):
            parts.append(
                f'<rect x="{x}" y="150" width="40" height="44" rx="3" fill="none" stroke="{D}" stroke-width="2.5"/>'
            )
    return "".join(parts)


def _tee(F, D, L, A):
    body = (
        "M130,84 L172,72 Q200,96 228,72 L270,84 L332,134 L304,170 L278,152 L282,420 L118,420 L122,152 L96,170 L68,134 Z"
    )
    return (
        f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
        f'<path d="M172,72 Q200,98 228,72" fill="none" stroke="{D}" stroke-width="5"/>'
    )


def _cami(F, D, L, A, long=False):
    hem = 465 if long else 400
    return (
        f'<path d="M160,62 L168,152 M240,62 L232,152" stroke="{D}" stroke-width="4"/>'
        f'<path d="M168,152 Q200,172 232,152 L{270 if long else 262},{hem} Q200,{hem + 14} {130 if long else 138},{hem} Z" '
        f'fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
        f'<path d="M210,180 Q222,300 214,{hem}" fill="none" stroke="{L}" stroke-width="7" opacity="0.6"/>'
    )


def _sweater(F, D, L, A):
    sl = "M136,92 L92,116 Q76,250 74,382 L112,386 Q120,262 132,190 Z"
    body = "M136,92 L172,82 Q200,100 228,82 L264,92 L278,190 L284,410 L116,410 L122,190 Z"
    parts = [f'<path d="{p}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>' for p in _sym(sl)]
    parts.append(f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>')
    parts.append(f'<path d="M172,82 Q200,104 228,82" fill="none" stroke="{D}" stroke-width="7"/>')
    parts.append(f'<rect x="116" y="386" width="168" height="24" fill="{A}" stroke="{D}" stroke-width="2"/>')
    for x in range(132, 272, 12):
        parts.append(f'<line x1="{x}" y1="120" x2="{x}" y2="384" stroke="{A}" stroke-width="2" opacity="0.6"/>')
    return "".join(parts)


def _trousers(F, D, L, A, wide=False, jeans=False):
    body = (
        "M120,60 L280,60 L318,462 L212,462 L200,175 L188,462 L82,462 Z"
        if wide
        else "M122,60 L278,60 L292,462 L214,462 L200,170 L186,462 L108,462 Z"
    )
    parts = [
        f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>',
        f'<rect x="{120 if wide else 122}" y="60" width="{160 if wide else 156}" height="22" fill="{A}" stroke="{D}" stroke-width="2.5"/>',
    ]
    if jeans:
        parts.append(
            f'<path d="M134,84 Q152,118 178,84 M222,84 Q248,118 266,84" fill="none" stroke="{L}" stroke-width="2.5" stroke-dasharray="5 4"/>'
        )
        parts.append(
            f'<path d="M200,82 L200,150 Q194,160 186,160" fill="none" stroke="{L}" stroke-width="2.5" stroke-dasharray="5 4"/>'
        )
        parts.append(f'<circle cx="200" cy="71" r="4" fill="{L}"/>')
    else:
        x1, x2 = (140, 260) if wide else (152, 248)
        parts.append(
            f'<path d="M{x1},90 L{x1 - (24 if wide else 6)},455 M{x2},90 L{x2 + (24 if wide else 6)},455" stroke="{A}" stroke-width="2"/>'
        )
    return "".join(parts)


def _skirt(F, D, L, A):
    return (
        f'<path d="M140,64 L260,64 L298,444 Q200,462 102,444 Z" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
        f'<rect x="140" y="64" width="120" height="16" fill="{A}" stroke="{D}" stroke-width="2"/>'
        f'<path d="M222,90 Q236,260 250,440" fill="none" stroke="{L}" stroke-width="10" opacity="0.55"/>'
        f'<path d="M168,100 Q160,280 150,446" fill="none" stroke="{A}" stroke-width="3"/>'
    )


def _dress(F, D, L, A):
    body = "M160,60 L186,60 L200,140 L214,60 L240,60 L262,90 L250,210 L304,452 Q200,470 96,452 L150,210 L138,90 Z"
    parts = [
        f'<path d="{p}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
        for p in _sym("M160,62 L122,90 L136,118 L148,102 Z")
    ]
    parts.append(f'<path d="{body}" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>')
    parts.append(f'<rect x="148" y="200" width="104" height="14" fill="{A}"/>')
    parts.append(
        f'<path d="M252,214 L262,262 M246,214 L240,266" stroke="{A}" stroke-width="6" stroke-linecap="round"/>'
    )
    parts.append(f'<path d="M236,214 L150,452" fill="none" stroke="{A}" stroke-width="3"/>')
    return "".join(parts)


def _shoe_pair(shape: str, F, D, L, A, sole: str):
    back_fill = shade(F, -0.08) if F.startswith("#") else F
    back = f'<g transform="translate(24,-118)">{shape.format(F=back_fill, D=D, L=L, S=sole)}</g>'
    front = f"<g>{shape.format(F=F, D=D, L=L, S=sole)}</g>"
    return back + front


_LOAFER = (
    '<path d="M60,330 Q60,292 110,288 L190,282 Q240,284 292,318 Q336,328 340,348 L340,360 L60,360 Z" '
    'fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="56" y="356" width="288" height="12" rx="4" fill="{S}"/>'
    '<path d="M168,292 Q210,312 252,298" fill="none" stroke="{D}" stroke-width="4"/>'
)
_SNEAKER = (
    '<path d="M60,330 Q60,282 120,278 L200,276 Q250,280 300,314 Q340,324 342,346 L342,356 L60,356 Z" '
    'fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="54" y="344" width="294" height="24" rx="10" fill="{S}" stroke="{D}" stroke-width="2.5"/>'
    '<path d="M180,286 L200,302 M198,284 L218,300 M216,286 L236,302" stroke="{D}" stroke-width="3"/>'
    '<path d="M60,300 L60,340 L84,340 L84,296 Z" fill="{L}"/>'
)
_BOOT = (
    '<path d="M90,170 L172,170 L180,286 Q240,294 300,316 Q332,328 334,350 L334,360 L84,360 L84,300 Z" '
    'fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
    '<rect x="80" y="356" width="258" height="12" rx="3" fill="{S}"/>'
    '<rect x="84" y="340" width="54" height="28" fill="{S}"/>'
    '<path d="M150,176 L156,280" stroke="{L}" stroke-width="3"/>'
)
_HEEL = (
    '<path d="M80,300 Q120,296 180,322 Q250,350 320,338 L330,352 Q250,372 170,352 L110,336 L104,420 L92,420 L90,320 Z" '
    'fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
    '<path d="M150,316 Q170,290 196,330 M230,346 Q250,318 270,344" fill="none" stroke="{F}" stroke-width="7"/>'
)


def _tote(F, D, L, A):
    return (
        f'<path d="M150,200 Q150,96 200,96 Q250,96 250,200" fill="none" stroke="{A}" stroke-width="13"/>'
        f'<path d="M100,196 L300,196 L322,436 L78,436 Z" fill="{F}" stroke="{D}" stroke-width="3" stroke-linejoin="round"/>'
        f'<path d="M104,222 L296,222" stroke="{A}" stroke-width="3" stroke-dasharray="6 5"/>'
        f'<rect x="186" y="232" width="28" height="18" rx="3" fill="{L}"/>'
    )


def _hat(F, D, L, A):
    return (
        f'<ellipse cx="200" cy="300" rx="170" ry="60" fill="{F}" stroke="{D}" stroke-width="3"/>'
        f'<path d="M130,300 Q130,170 200,170 Q270,170 270,300 Z" fill="{F}" stroke="{D}" stroke-width="3"/>'
        f'<path d="M132,272 Q200,290 268,272 L270,290 Q200,308 130,290 Z" fill="{A}"/>'
    )


def _earrings(F, D, L, A):
    return (
        f'<circle cx="140" cy="250" r="62" fill="none" stroke="{F}" stroke-width="14"/>'
        f'<circle cx="270" cy="250" r="62" fill="none" stroke="{F}" stroke-width="14"/>'
        f'<circle cx="140" cy="250" r="62" fill="none" stroke="{L}" stroke-width="3" opacity="0.7"/>'
        f'<circle cx="270" cy="250" r="62" fill="none" stroke="{L}" stroke-width="3" opacity="0.7"/>'
    )


SHAPES = {
    "blazer": lambda F, D, L, A: _blazer(F, D, L, A),
    "trench": lambda F, D, L, A: _blazer(F, D, L, A, long=True),
    "jacket": lambda F, D, L, A: _jacket(F, D, L, A),
    "leather_jacket": lambda F, D, L, A: _jacket(F, D, L, A, leather=True),
    "cardigan": _cardigan,
    "shirt": _shirt,
    "overshirt": lambda F, D, L, A: _shirt(F, D, L, A, boxy=True),
    "tee": _tee,
    "cami": _cami,
    "slip_dress": lambda F, D, L, A: _cami(F, D, L, A, long=True),
    "sweater": _sweater,
    "trousers": _trousers,
    "wide_trousers": lambda F, D, L, A: _trousers(F, D, L, A, wide=True),
    "jeans": lambda F, D, L, A: _trousers(F, D, L, A, jeans=True),
    "skirt": _skirt,
    "dress": _dress,
    "loafers": lambda F, D, L, A: _shoe_pair(_LOAFER, F, D, L, A, sole=D),
    "sneakers": lambda F, D, L, A: _shoe_pair(_SNEAKER, F, D, L, A, sole="#f4f1ea"),
    "boots": lambda F, D, L, A: _shoe_pair(_BOOT, F, D, L, A, sole=D),
    "heels": lambda F, D, L, A: _shoe_pair(_HEEL, F, D, L, A, sole=D),
    "tote": _tote,
    "hat": _hat,
    "earrings": _earrings,
}


def garment_svg_inner(
    shape: str, color: str, accent: str | None = None, stripes: str | None = None, uid: str = "g"
) -> str:
    D = shade(color, -0.42)
    L = accent or shade(color, 0.35)
    A = shade(color, -0.14)
    F = f"url(#{uid}-st)" if stripes else color
    defs = ""
    if stripes:
        defs = (
            f'<defs><pattern id="{uid}-st" width="24" height="24" patternUnits="userSpaceOnUse">'
            f'<rect width="24" height="24" fill="{color}"/><rect width="24" height="9" fill="{stripes}"/>'
            f"</pattern></defs>"
        )
    return defs + SHAPES[shape](F, D, L, A)


def garment_svg(shape: str, color: str, accent: str | None = None, stripes: str | None = None, title: str = "") -> str:
    inner = garment_svg_inner(shape, color, accent, stripes, uid="g")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img">'
        f"<title>{escape(title)}</title>{inner}</svg>"
    )


def composite_svg(placements: list[dict], background: str = "#efe8dc", width: int = 900, height: int = 1100) -> str:
    """Flat-lay board: placements = [{shape, color, accent?, stripes?, x, y, w}] (h = w*1.25)."""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        f'<rect width="{width}" height="{height}" fill="{background}"/>',
    ]
    for i, p in enumerate(placements):
        w = p["w"]
        inner = garment_svg_inner(p["shape"], p["color"], p.get("accent"), p.get("stripes"), uid=f"p{i}")
        parts.append(
            f'<svg x="{p["x"]}" y="{p["y"]}" width="{w}" height="{w * 1.25}" viewBox="0 0 {W} {H}">{inner}</svg>'
        )
    parts.append("</svg>")
    return "".join(parts)

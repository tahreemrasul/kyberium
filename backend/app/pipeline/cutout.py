"""Consistent garment display images: crop to the garment, remove plain backgrounds, and place the
ORIGINAL pixels at a standard scale on the studio background.

1. Gemini returns a bounding box for the main garment (small, fast structured output).
2. If the area around the garment is a near-uniform backdrop (product shots, flat lays), it is
   removed deterministically by flood-filling from the edges. Busy backgrounds (e.g. a mirror
   selfie) are kept as a tight crop rather than risking a bad cut.
3. The result is scaled so its longest side fills a fixed share of a 4:5 cream canvas.

Nothing is generated or retouched, so the image never misrepresents what the user owns. Any failure
falls back to padding the photo into the same frame — uploads are never blocked.
"""

import io
import logging

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat
from pydantic import BaseModel, Field

from app.ai.client import AIError, GeminiClient

log = logging.getLogger("rewear.cutout")

CANVAS = (800, 1000)  # 4:5, matches the closet cards
BACKGROUND = (239, 232, 218)  # studio "well" cream (#efe8da)
FILL = 0.84  # the garment's longest side fills 84% of the canvas
SENTINEL = (255, 0, 254)

BOX_SYSTEM = (
    "You locate clothing in photos. Return the bounding box of the single main clothing item "
    "(if a person wears several garments, the most prominent one), as box_2d = [y0, x0, y1, x1] "
    "normalised to 0-1000. Include the whole garment; exclude the person's face, hands and the background."
)


class GarmentBox(BaseModel):
    box_2d: list[int] = Field(min_length=4, max_length=4)
    label: str = ""


def _crop_box(img: Image.Image, box: list[int], pad: float = 0.04) -> Image.Image:
    y0, x0, y1, x1 = (max(0, min(1000, v)) for v in box)
    if x1 - x0 < 20 or y1 - y0 < 20:
        return img
    w, h = img.size
    px, py = int((x1 - x0) / 1000 * w * pad), int((y1 - y0) / 1000 * h * pad)
    return img.crop(
        (
            max(0, int(x0 / 1000 * w) - px),
            max(0, int(y0 / 1000 * h) - py),
            min(w, int(x1 / 1000 * w) + px),
            min(h, int(y1 / 1000 * h) + py),
        )
    )


def plain_background_mask(img: Image.Image, tolerance: int = 44) -> Image.Image | None:
    """Alpha mask that removes a near-uniform backdrop, or None if the background is busy."""
    rgb = img.convert("RGB")
    w, h = rgb.size
    border = Image.new("RGB", (w * 2 + h * 2, 1))
    border.paste(rgb.crop((0, 0, w, 1)), (0, 0))
    border.paste(rgb.crop((0, h - 1, w, h)), (w, 0))
    border.paste(rgb.crop((0, 0, 1, h)).rotate(90, expand=True), (2 * w, 0))
    border.paste(rgb.crop((w - 1, 0, w, h)).rotate(90, expand=True), (2 * w + h, 0))
    if max(ImageStat.Stat(border).stddev) > 30:  # busy edges (e.g. a room): don't attempt a cut
        return None
    filled = rgb.copy()
    seeds = [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (w // 2, 0), (w // 2, h - 1), (0, h // 2), (w - 1, h // 2)]
    for seed in seeds:
        if filled.getpixel(seed) != SENTINEL:
            ImageDraw.floodfill(filled, seed, SENTINEL, thresh=tolerance)
    diff = ImageChops.difference(filled, Image.new("RGB", (w, h), SENTINEL)).convert("L")
    mask = diff.point(lambda v: 255 if v > 0 else 0)
    mask = mask.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1))
    coverage = sum(mask.histogram()[128:]) / (w * h)
    if not 0.08 < coverage < 0.97:
        return None
    bbox = mask.point(lambda v: 255 if v > 127 else 0).getbbox()
    if bbox:
        touching = (bbox[0] <= 1) + (bbox[1] <= 1) + (bbox[2] >= w - 1) + (bbox[3] >= h - 1)
        if touching >= 2:  # leftover backdrop (e.g. a screenshot margin) still reaches the edges
            return None
    return mask


def place_on_canvas(img: Image.Image, mask: Image.Image | None = None) -> bytes:
    """Scale the (optionally masked) garment to a standard size and centre it on the studio background."""
    rgba = img.convert("RGBA")
    if mask is not None:
        rgba.putalpha(mask.convert("L"))
        bbox = mask.convert("L").point(lambda v: 255 if v > 24 else 0).getbbox()
        if bbox:
            rgba = rgba.crop(bbox)
    max_w, max_h = int(CANVAS[0] * FILL), int(CANVAS[1] * FILL)
    scale = min(max_w / rgba.width, max_h / rgba.height)
    rgba = rgba.resize((max(1, int(rgba.width * scale)), max(1, int(rgba.height * scale))), Image.LANCZOS)
    canvas = Image.new("RGB", CANVAS, BACKGROUND)
    canvas.paste(rgba, ((CANVAS[0] - rgba.width) // 2, (CANVAS[1] - rgba.height) // 2), rgba)
    out = io.BytesIO()
    canvas.save(out, format="PNG", optimize=True)
    return out.getvalue()


async def locate(ai: GeminiClient, jpeg: bytes) -> list[int] | None:
    try:
        box = await ai.generate_json(
            schema=GarmentBox,
            system=BOX_SYSTEM,
            contents=[ai.image_part(jpeg, "image/jpeg"), "Locate the garment."],
            temperature=0.0,
            thinking_budget=0,
            label="garment_box",
        )
        return box.box_2d
    except AIError as exc:  # display polish must never block an upload
        log.warning("garment localisation failed: %s", exc.message)
        return None


def _try_cutout(img: Image.Image) -> bytes | None:
    # Strict tolerance first (protects light garments on light backdrops), looser for gradients.
    for tolerance in (30, 44):
        mask = plain_background_mask(img, tolerance)
        if mask is not None:
            return place_on_canvas(img, mask)
    return None


async def display_image(ai: GeminiClient | None, jpeg: bytes) -> tuple[bytes, str]:
    """Return (png_bytes, method) where method is 'cutout', 'crop' or 'padded'. Always succeeds."""
    img = Image.open(io.BytesIO(jpeg)).convert("RGB")
    try:
        # Product shots / flat lays: the plain backdrop itself defines the garment's outline.
        if (png := _try_cutout(img)) is not None:
            return png, "cutout"
    except Exception as exc:
        log.warning("background removal failed: %s", exc)
    # Otherwise let Gemini locate the garment, then retry on the tight region (screenshot margins,
    # busy rooms). If the backdrop is still busy, keep the tight crop as-is.
    box = await locate(ai, jpeg) if ai is not None else None
    region = _crop_box(img, box) if box else img
    if box:
        try:
            if (png := _try_cutout(region)) is not None:
                return png, "cutout"
        except Exception as exc:
            log.warning("background removal on crop failed: %s", exc)
    return place_on_canvas(region), "crop" if box else "padded"
